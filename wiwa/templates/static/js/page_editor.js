// パスとファイル名: wiwa/templates/js/admin/page_editor.js

document.addEventListener("DOMContentLoaded", function(){
    const form = document.getElementById("page-form");
    const editorHolder = document.getElementById("editorjs");
    const bodyJsonInput = document.getElementById("body_json");
    const initialDataElement = document.getElementById("editorjs-initial-data");

    if (!form || !editorHolder || !bodyJsonInput) {
        return;
    }

    let initialData = {
        blocks: []
    };

    if (initialDataElement) {
        try {
            initialData = JSON.parse(initialDataElement.textContent);
        } catch (error) {
            initialData = {
                blocks: []
            };
        }
    }

    const editor = new EditorJS({
        holder: "editorjs",
        tools: {
            header: Header,
            list: EditorjsList
        },
        data: initialData
    });

    form.addEventListener("submit", function(event){
        event.preventDefault();

        editor.save().then(function(outputData){
            bodyJsonInput.value = JSON.stringify(outputData);
            form.submit();
        });
    });
});