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

from chartjs.views.lines import BaseLineChartView

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy

from django.utils.translation import ugettext_lazy as _
from django.views import generic

from horizon import forms
from horizon import tables

from mistraldashboard import api
from mistraldashboard.delayt_workloads import forms as mistral_forms
from mistraldashboard.delayt_workloads.tables import \
    DelayTolerantWorkloadsTable


class LineChartJSONView(BaseLineChartView):

    def get_labels(self):
        """Return 7 labels."""
        return ["January", "February", "March", "April", "May", "June", "July"]

    def get_data(self):
        """Return 3 datasets to plot."""

        return [[75, 44, 92, 11, 44, 95, 35],
                [41, 92, 18, 3, 73, 87, 92],
                [87, 21, 94, 3, 90, 13, 65]]


class ChartView(generic.TemplateView):
    template_name = 'mistral/delayt_workloads/chart.html'


class OverviewView(generic.TemplateView):
    template_name = 'mistral/delayt_workloads/detail.html'
    page_title = _("Delay Tolerant Workloads Details")
    workflow_url = 'horizon:mistral:workflows:detail'
    list_url = 'horizon:mistral:delayt_workloads:index'

    def get_context_data(self, **kwargs):
        context = super(OverviewView, self).get_context_data(**kwargs)
        delay_tolerant_workload = {}
        delay_tolerant_workload = api.delay_tolerant_workload_get(
            self.request,
            kwargs['delay_tolerant_workload_name']
        )
        delay_tolerant_workload.workflow_url = reverse(
            self.workflow_url,
            args=[delay_tolerant_workload.workflow_name]
        )
        delay_tolerant_workload.list_url = reverse_lazy(self.list_url)
        context['delay_tolerant_workload'] = delay_tolerant_workload

        return context


class CreateView(forms.ModalFormView):
    template_name = 'mistral/delayt_workloads/create.html'
    modal_header = _("Create Delay Tolerant Workload")
    form_id = "create_delayt_workload"
    form_class = mistral_forms.CreateForm
    submit_label = _("Create Delay Tolerant Workload")
    submit_url = reverse_lazy("horizon:mistral:delayt_workloads:create")
    success_url = reverse_lazy('horizon:mistral:delayt_workloads:index')
    page_title = _("Create Delay Tolerant Workload")

    def get_form_kwargs(self):
        kwargs = super(CreateView, self).get_form_kwargs()

        return kwargs


class IndexView(tables.DataTableView):
    table_class = DelayTolerantWorkloadsTable
    template_name = 'mistral/delayt_workloads/index.html'

    def get_data(self):
        return api.delay_tolerant_workload_list(self.request)
