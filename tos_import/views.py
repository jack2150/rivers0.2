from datetime import datetime
import glob
import os
from django import forms
from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldError
from django.core.urlresolvers import reverse
from django.shortcuts import render
from pandas.tseries.offsets import BDay
from rivers.settings import BASE_DIR
from statistic.simple.stat_day.models import SaveStatDay
from tos_import.models import Statement
from tos_import.statement.statement_account.models import SaveAccountStatement
from tos_import.statement.statement_position.models import SavePositionStatement
from tos_import.statement.statement_trade.models import SaveTradeActivity


import_path = '%s/tos_import/files/real_files/' % BASE_DIR


class AccountStatementFile(forms.FileField):
    def validate(self, value):
        """
        Validate file name of account statement file
        :param value: dict
        """
        super(AccountStatementFile, self).validate(value)

        fname = os.path.basename(value.name)
        validate_filename(fname, 'AccountStatement')


class PositionStatementFile(forms.FileField):
    def validate(self, value):
        """
        Validate file name of position statement file
        :param value: dict
        """
        super(PositionStatementFile, self).validate(value)

        fname = os.path.basename(value.name)
        validate_filename(fname, 'PositionStatement')


class TradeActivityFile(forms.FileField):
    def validate(self, value):
        """
        Validate file name of position file
        :param value: dict
        """
        super(TradeActivityFile, self).validate(value)

        fname = os.path.basename(value.name)
        validate_filename(fname, 'TradeActivity')


def validate_filename(fname, validate_str):
    """
    Validate filename for all statements
    :param fname: str
    :param validate_str: str
    :return: None
    """
    if validate_str in fname:
        try:
            datetime.strptime(fname[:10], '%Y-%m-%d')
        except ValueError:
            raise forms.ValidationError('Incorrect file date: %s' % fname)

        if fname.split('.', 1)[1] != 'csv':
            raise forms.ValidationError('Incorrect file extension: %s' % fname)
    else:
        raise forms.ValidationError('Incorrect filename: %s' % fname)


class PmsImportStatementsForm(forms.Form):
    date = forms.DateField()

    account_statement = AccountStatementFile(
        label='Account Statement'
    )

    position_statement = PositionStatementFile(
        label='Position Statement'
    )

    trade_activity = TradeActivityFile(
        label='Trace Activity'
    )

    def clean(self):
        """
        Validate date for file date and all import file name date
        """
        cleaned_data = super(PmsImportStatementsForm, self).clean()

        if not len(self._errors):
            # no error found for field
            file_date = cleaned_data.get("date").strftime('%Y-%m-%d')

            acc_date = datetime.strptime(
                cleaned_data.get("account_statement").name[:10], '%Y-%m-%d'
            )
            pos_date = datetime.strptime(
                cleaned_data.get("position_statement").name[:10], '%Y-%m-%d'
            )
            ta_date = datetime.strptime(
                cleaned_data.get("trade_activity").name[:10], '%Y-%m-%d'
            )

            acc_date = acc_date - BDay(1)
            acc_date = acc_date.strftime('%Y-%m-%d')
            pos_date = pos_date - BDay(1)
            pos_date = pos_date.strftime('%Y-%m-%d')
            ta_date = ta_date - BDay(1)
            ta_date = ta_date.strftime('%Y-%m-%d')

            if acc_date == pos_date == ta_date:
                if file_date != acc_date:
                    error_message = 'All date must have (-1 BDay, %s != %s).' % (file_date, acc_date)
                    self._errors['date'] = self.error_class([error_message])
            else:
                error_message = 'All file date must be same.'
                self._errors['date'] = self.error_class([error_message])

            if not len(self._errors):
                # save here so django can track error location
                acc_data = cleaned_data.get("account_statement")
                acc_data = acc_data.read()
                pos_data = cleaned_data.get("position_statement")
                pos_data = pos_data.read()
                ta_data = cleaned_data.get("trade_activity")
                ta_data = ta_data.read()

                statement = Statement()
                statement.date = file_date
                statement.account_statement = acc_data
                statement.position_statement = pos_data
                statement.trade_activity = ta_data
                statement.save()

                SaveAccountStatement(
                    date=file_date,
                    statement=statement,
                    file_data=acc_data
                ).save_all()

                SavePositionStatement(
                    date=file_date,
                    statement=statement,
                    file_data=pos_data
                ).save_all()

                SaveTradeActivity(
                    date=file_date,
                    statement=statement,
                    file_data=ta_data
                ).save_all()

                SaveStatDay(statement).save_all()

                self.cleaned_data['statement_id'] = statement.id
                self.cleaned_data['statement_name'] = statement.__unicode__()

        return cleaned_data


@staff_member_required
def statement_import(request, statement_id=0):
    # custom view which should return an HttpResponse
    # return HttpResponse('something')
    template = 'tos_import/statement_import.html'

    if request.method == 'POST':
        try:
            import_statement_form = PmsImportStatementsForm(request.POST, request.FILES)
        except Exception:
            raise FieldError('Import statement form error.')

        if import_statement_form.is_valid():
            # log import

            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=ContentType.objects.get_for_model(Statement).id,
                object_id=import_statement_form.cleaned_data['statement_id'],
                object_repr=import_statement_form.cleaned_data['statement_name'],
                action_flag=ADDITION
            )

            statement_id = import_statement_form.cleaned_data['statement_id']
    else:
        import_statement_form = PmsImportStatementsForm()

    parameters = dict(
        request=request,
        form=import_statement_form,
        statement_id=statement_id
    )

    return render(request, template, parameters)


@staff_member_required
def statement_import_all(request):
    """
    import all statements in real_path folder
    :param request: request
    :return: render
    """
    template = 'tos_import/statement_import_all.html'
    real_files_folder = glob.glob('%s/*' % import_path)

    imported_logs = list()
    error_logs = list()
    for folder in real_files_folder:
        if os.path.isdir(folder):
            real_date = os.path.basename(folder)

            try:
                datetime.strptime(real_date, '%Y-%m-%d')
            except ValueError:
                error_logs.append(
                    {
                        'path': folder,
                        'date': real_date.split(' ')[0],
                        'note': real_date.split(' ')[1],
                        'error': 'Invalid filename'
                    }
                )
            else:
                # only import error free folder
                # get file inside and get date
                # skip date exist in db
                if not Statement.objects.filter(date=real_date).exists():
                    statement = glob.glob('%s/*.csv' % folder)[0]
                    file_date = os.path.basename(statement)[0:10]

                    acc_data = open(os.path.join(
                        folder, '%s-AccountStatement.csv' % file_date)
                    ).read()
                    pos_data = open(os.path.join(
                        folder, '%s-PositionStatement.csv' % file_date)
                    ).read()
                    ta_data = open(os.path.join(
                        folder, '%s-TradeActivity.csv' % file_date)
                    ).read()

                    statement = Statement()
                    statement.date = real_date
                    statement.account_statement = acc_data
                    statement.position_statement = pos_data
                    statement.trade_activity = ta_data
                    statement.save()

                    account_summary_id = SaveAccountStatement(
                        date=file_date,
                        statement=statement,
                        file_data=acc_data
                    ).save_all()

                    position_summary_id = SavePositionStatement(
                        date=file_date,
                        statement=statement,
                        file_data=pos_data
                    ).save_all()

                    trade_summary_id = SaveTradeActivity(
                        date=file_date,
                        statement=statement,
                        file_data=ta_data
                    ).save_all()

                    # save stat day
                    SaveStatDay(statement).save_all()

                    imported_logs.append({
                        'statement': {
                            'id': statement.id,
                            'change_url': reverse(
                                'admin:tos_import_statement_change',
                                args={statement.id}),
                            'delete_url': reverse(
                                'admin:tos_import_statement_delete',
                                args={statement.id}),
                            'date': statement.date
                        },
                        'account_statement': {
                            'id': account_summary_id,
                            'change_url': reverse(
                                'admin:statement_account_accountsummary_change',
                                args={account_summary_id}),
                            'delete_url': reverse(
                                'admin:statement_account_accountsummary_delete',
                                args={account_summary_id}),
                        },
                        'position_statement': {
                            'id': position_summary_id,
                            'change_url': reverse(
                                'admin:statement_position_positionsummary_change',
                                args={position_summary_id}),
                            'delete_url': reverse(
                                'admin:statement_position_positionsummary_delete',
                                args={position_summary_id}),
                        },
                        'trade_activity': {
                            'id': trade_summary_id,
                            'change_url': reverse(
                                'admin:statement_trade_tradesummary_change',
                                args={trade_summary_id}),
                            'delete_url': reverse(
                                'admin:statement_trade_tradesummary_delete',
                                args={trade_summary_id}),
                        },
                    })

                    # log entry
                    LogEntry.objects.log_action(
                        user_id=request.user.id,
                        content_type_id=ContentType.objects.get_for_model(Statement).id,
                        object_id=statement.id,
                        object_repr=statement.__unicode__(),
                        action_flag=ADDITION
                    )

    parameters = dict(
        imported_logs=imported_logs,
        error_logs=error_logs
    )

    # testing page view, delete all after done...
    # Statement.objects.all().delete()

    return render(request, template, parameters)
