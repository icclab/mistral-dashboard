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

import random

from mistraldashboard import api
from mistraldashboard.delayt_workloads import forms as mistral_forms
from mistraldashboard.delayt_workloads.tables import \
    DelayTolerantWorkloadsTable


class SamplesView(generic.TemplateView):
    def get(self, request, *args, **kwargs):
        rand = [random.randint(0, 100) for r in xrange(12)]
        average = reduce(lambda x, y: x + y, rand, 0) / 12
        used = rand[11]

        ret = {}
        ret['series'] = [
            {"data": [{"y": rand[0], "x": "2013-11-08T09:57:53"},
                      {"y": rand[1], "x": "2013-11-09T09:57:53"},
                      {"y": rand[2], "x": "2013-11-10T09:57:53"},
                      {"y": rand[3], "x": "2013-11-11T09:57:53"},
                      {"y": rand[4], "x": "2013-11-12T09:57:53"},
                      {"y": rand[5], "x": "2013-11-13T09:57:53"},
                      {"y": rand[6], "x": "2013-11-14T09:57:53"},
                      {"y": rand[7], "x": "2013-11-15T09:57:53"},
                      {"y": rand[8], "x": "2013-11-16T09:57:53"},
                      {"y": rand[9], "x": "2013-11-17T09:57:53"},
                      {"y": rand[10], "x": "2013-11-18T09:57:53"},
                      {"y": rand[11], "x": "2013-11-19T09:57:53"}],
            "name": "admin", "unit": "%"}]

        ret['settings'] = {
            'renderer': 'StaticAxes',
            'yMin': 0,
            'yMax': 100,
            'higlight_last_point': True,
            "auto_size": False, 'auto_resize': False,
            "axes_x": False, "axes_y": False,
            'bar_chart_settings': {
                'orientation': 'vertical',
                'used_label_placement': 'left',
                'width': 30,
                'color_scale_domain': [0, 80, 80, 100],
                'color_scale_range': [
                    '#00FE00', '#00FF00', '#FE0000', '#FF0000'],
                'average_color_scale_domain': [0, 100],
                'average_color_scale_range': [
                    '#0000FF', '#0000FF']
            }
        }

        tooltip_average = "Average %s &percnt;<br> From: %s, to: %s" % (
            used, '2013-11-08T09:57:53', '2013-11-19T09:57:53')

        ret['stats'] = {
            'average': average,
            'used': used,
            'tooltip_average': tooltip_average
        }

        return HttpResponse(json.dumps(ret),
            mimetype='application/json')


class LineChartJSONView(BaseLineChartView):

    def get_labels(self):
        delay_tolerant_workloads = api.delay_tolerant_workload_list(
            self.request)

        data = []
        if delay_tolerant_workloads:
            for dtw in delay_tolerant_workloads:
                if dtw.created_at.split(' ')[0] not in data:
                    data.append(dtw.created_at.split(' ')[0])

        return data

    def get_data(self):
        """Return 3 datasets to plot."""
        delay_tolerant_workloads = api.delay_tolerant_workload_list(
            self.request)

        data = {}
        if delay_tolerant_workloads:
            for dtw in delay_tolerant_workloads:
                created_at = dtw.created_at.split(' ')[0]
                if created_at in data.keys():
                    data[created_at] += 1
                else:
                    data[created_at] = 1
        return [data.values()]


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
