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

from django.core.urlresolvers import reverse

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from horizon import tables

from mistraldashboard import api
from mistraldashboard.default.utils import humantime


class CreateDelayTolerantWorkload(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Delay Tolerant Workload")
    url = "horizon:mistral:delay_tolerant_workloads:create"
    classes = ("ajax-modal",)
    icon = "plus"


class DeleteDelayTolerantWorkload(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Delay Tolerant Workload",
            u"Delete Delay Tolerant Workloads",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Delay Tolerant Workload",
            u"Deleted Delay Tolerant Workloads",
            count
        )

    def delete(self, request, delay_tolerant_workload_name):
        api.delay_tolerant_wokload_delete(request,
                                          delay_tolerant_workload_name)


class WorkflowColumn(tables.Column):
    def get_link_url(self, datum):
        workflow_url = "horizon:mistral:workflows:detail"
        obj_id = datum.workflow_name
        return reverse(workflow_url, args=[obj_id])


class CronTriggersTable(tables.DataTable):
    id = tables.Column(
        "id",
        verbose_name=_("ID"),
        link="horizon:mistral:cron_triggers:detail"
    )
    name = tables.Column(
        "name",
        verbose_name=_("Name")
    )
    workflow_name = WorkflowColumn(
        "workflow_name",
        verbose_name=_("Workflow"),
        link=True
    )
    deadline = tables.Column(
        "deadline",
        verbose_name=_("Deadline"),
    )
    job_duration = tables.Column(
        "job_duration",
        verbose_name=_("Job Duration"),
    )
    created_at = tables.Column(
        "created_at",
        verbose_name=_("Created at"),
        filters=[humantime]
    )
    updated_at = tables.Column(
        "updated_at",
        verbose_name=_("Updated at"),
        filters=[humantime]
    )

    def get_object_id(self, datum):
        return datum.name

    class Meta(object):
        name = "cron trigger"
        verbose_name = _("Delay tolerant Workload")
        table_actions = (
            tables.FilterAction,
            CreateDelayTolerantWorkload,
            DeleteDelayTolerantWorkload
        )
        row_actions = (DeleteDelayTolerantWorkload,)
