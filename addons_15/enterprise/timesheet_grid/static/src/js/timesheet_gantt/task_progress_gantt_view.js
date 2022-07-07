/** @odoo-module **/

import TaskGanttRow from '@project_enterprise/js/task_gantt_row';
import fieldUtils from 'web.field_utils';

TaskGanttRow.include({
    _getPopoverContext: function () {
        const data = this._super.apply(this, arguments);
        if (data.allow_subtasks) {
            data.total_hours_spent_formatted = fieldUtils.format.timesheet_uom(data.total_hours_spent);
        } else {
            data.effective_hours_formatted = fieldUtils.format.timesheet_uom(data.effective_hours);
        }
        data.progressFormatted = Math.round(data.progress);
        return data;
    },
});
