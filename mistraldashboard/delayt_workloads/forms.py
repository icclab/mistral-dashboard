# Copyright (c) 2016. Zuercher Hochschule fuer Angewandte Wissenschaften
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import json

from django.utils.translation import ugettext_lazy as _

from horizon import forms
from horizon import messages

from mistraldashboard import api
from mistraldashboard.default.utils import convert_empty_string_to_none
from mistraldashboard.handle_errors import handle_errors


class CreateForm(forms.SelfHandlingForm):
    name = forms.CharField(
        max_length=255,
        label=_("Name"),
        help_text=_('Delay Tolerant Workload name.'),
        required=True
    )

    workflow_id = forms.ChoiceField(
        label=_('Workflow ID'),
        help_text=_('Select Workflow ID.'),
        widget=forms.Select(
            attrs={'class': 'switchable',
                   'data-slug': 'workflow_select'}
        )
    )

    input_source = forms.ChoiceField(
        label=_('Input'),
        help_text=_('JSON of input values defined in the workflow. '
                    'Select either file or raw content.'),
        choices=[('file', _('File')),
                 ('raw', _('Direct Input'))],
        widget=forms.Select(
            attrs={'class': 'switchable',
                   'data-slug': 'inputsource'}
        )
    )
    input_upload = forms.FileField(
        label=_('Input File'),
        help_text=_('A local input to upload.'),
        widget=forms.FileInput(
            attrs={'class': 'switched',
                   'data-switch-on': 'inputsource',
                   'data-inputsource-file': _('Input File')}
        ),
        required=False
    )
    input_data = forms.CharField(
        label=_('Input Data'),
        help_text=_('The raw contents of the input.'),
        widget=forms.widgets.Textarea(
            attrs={'class': 'switched',
                   'data-switch-on': 'inputsource',
                   'data-inputsource-raw': _('Input Data'),
                   'rows': 4}
        ),
        required=False
    )

    params_source = forms.ChoiceField(
        label=_('Params'),
        help_text=_('JSON of params values defined in the workflow. '
                    'Select either file or raw content.'),
        choices=[('file', _('File')),
                 ('raw', _('Direct Input'))],
        widget=forms.Select(
            attrs={'class': 'switchable',
                   'data-slug': 'paramssource'}
        )
    )
    params_upload = forms.FileField(
        label=_('Params File'),
        help_text=_('A local input to upload.'),
        widget=forms.FileInput(
            attrs={'class': 'switched',
                   'data-switch-on': 'paramssource',
                   'data-paramssource-file': _('Params File')}
        ),
        required=False
    )
    params_data = forms.CharField(
        label=_('Params Data'),
        help_text=_('The raw contents of the params.'),
        widget=forms.widgets.Textarea(
            attrs={'class': 'switched',
                   'data-switch-on': 'paramssource',
                   'data-paramssource-raw': _('Params Data'),
                   'rows': 4}
        ),
        required=False
    )
    deadline = forms.CharField(
        label=_('Deadline (YYYY-MM-DDTHH:MM:SS)'),
        help_text=_('Date and time of the deadline.'),
        widget=forms.widgets.TextInput(),
        required=True
    )
    job_duration = forms.CharField(
        label=_('Job Duration (Minutes)'),
        help_text=_('Approximated time to execute the workflow.'),
        widget=forms.widgets.TextInput(),
        required=True
    )

    def __init__(self, request, *args, **kwargs):
        super(CreateForm, self).__init__(request, *args, **kwargs)
        workflow_list = api.workflow_list(request)
        workflow_id_list = []
        for wf in workflow_list:
            workflow_id_list.append(
                (wf.id, "{id} ({name})".format(id=wf.id, name=wf.name))
            )

        self.fields['workflow_id'].choices = workflow_id_list

    def clean(self):
        cleaned_data = super(CreateForm, self).clean()
        cleaned_data['input'] = ""
        cleaned_data['params'] = ""

        if cleaned_data.get('input_upload'):
            files = self.request.FILES
            cleaned_data['input'] = files['input_upload'].read()
        elif cleaned_data.get('input_data'):
            cleaned_data['input'] = cleaned_data['input_data']

        del(cleaned_data['input_upload'])
        del(cleaned_data['input_data'])

        if len(cleaned_data['input']) > 0:
            try:
                cleaned_data['input'] = json.loads(cleaned_data['input'])
            except Exception as e:
                msg = _('Input is invalid JSON: %s') % str(e)
                raise forms.ValidationError(msg)

        if cleaned_data.get('params_upload'):
            files = self.request.FILES
            cleaned_data['params'] = files['params_upload'].read()
        elif cleaned_data.get('params_data'):
            cleaned_data['params'] = cleaned_data['params_data']

        del(cleaned_data['params_upload'])
        del(cleaned_data['params_data'])

        if len(cleaned_data['params']) > 0:
            try:
                cleaned_data['params'] = json.loads(cleaned_data['params'])
            except Exception as e:
                msg = _('Params is invalid JSON: %s') % str(e)
                raise forms.ValidationError(msg)

        return cleaned_data

    @handle_errors(_("Unable to create Delay Tolerant Workload"), [])
    def handle(self, request, data):
        data['input'] = convert_empty_string_to_none(data['input'])
        data['params'] = convert_empty_string_to_none(data['params'])
        data['schedule_pattern'] = convert_empty_string_to_none(
            data['schedule_pattern']
        )
        data['deadline'] = convert_empty_string_to_none(data['deadline'])
        data['job_duration'] = convert_empty_string_to_none(
            data['job_duration']
        )

        try:
            api.delay_tolerant_wokload_create(
                request,
                data['name'],
                data['workflow_id'],
                data['input'],
                data['params'],
                data['job_duration'],
                data['deadline'],
            )
            msg = _('Successfully created Delay Tolerant Workload.')
            messages.success(request, msg)

            return True

        finally:
            pass
