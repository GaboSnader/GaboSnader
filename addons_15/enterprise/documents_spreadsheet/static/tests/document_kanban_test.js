/** @odoo-module */

import { nextTick, dom } from "web.test_utils";
import DocumentsKanbanView from "documents_spreadsheet.KanbanView";
import { createDocumentsView } from "documents.test_utils";
import { afterEach, beforeEach } from "@mail/utils/test_utils";
import { getBasicData } from "./spreadsheet_test_data";
const { module, test } = QUnit;

module("documents_spreadsheet kanban", {
    beforeEach: function () {
        beforeEach(this);
        this.data = {
            ...this.data,
            ...getBasicData(),
        };
    },
    afterEach: function () {
        afterEach(this);
    },
});

test("thumbnail size in document side panel", async function (assert) {
    assert.expect(9);
    this.data["documents.document"].records.push({
        id: 3,
        name: "",
        raw: "{}",
        folder_id: 1,
        handler: "spreadsheet",
    });
    const kanban = await createDocumentsView({
        View: DocumentsKanbanView,
        model: "documents.document",
        data: this.data,
        arch: `
          <kanban><templates><t t-name="kanban-box">
              <div>
                  <i class="fa fa-circle-thin o_record_selector"/>
                  <field name="name"/>
                  <field name="handler"/>
              </div>
          </t></templates></kanban>
      `,
    });
    await dom.click(".o_kanban_record:nth(0) .o_record_selector");
    await nextTick();
    assert.containsOnce(kanban, ".o_documents_inspector_preview .o_document_preview");
    assert.equal(
        dom.find(kanban, ".o_documents_inspector_preview .o_document_preview img").dataset.src,
        "/documents/image/1/268x130?field=thumbnail&unique="
    );
    await dom.click(".o_kanban_record:nth(1) .o_record_selector");
    await nextTick();
    assert.containsN(kanban, ".o_documents_inspector_preview .o_document_preview", 2);
    let previews = kanban.el.querySelectorAll(
        ".o_documents_inspector_preview .o_document_preview img"
    );
    assert.equal(previews[0].dataset.src, "/documents/image/1/120x130?field=thumbnail&unique=");
    assert.equal(previews[1].dataset.src, "/documents/image/2/120x130?field=thumbnail&unique=");
    await dom.click(".o_kanban_record:nth(2) .o_record_selector");
    await nextTick();
    assert.containsN(kanban, ".o_documents_inspector_preview .o_document_preview", 3);
    previews = kanban.el.querySelectorAll(".o_documents_inspector_preview .o_document_preview img");
    assert.equal(previews[0].dataset.src, "/documents/image/1/120x75?field=thumbnail&unique=");
    assert.equal(previews[1].dataset.src, "/documents/image/2/120x75?field=thumbnail&unique=");
    assert.equal(previews[2].dataset.src, "/documents/image/3/120x75?field=thumbnail&unique=");
    kanban.destroy();
});
