// パスとファイル名: wiwa/templates/js/admin/page_editor.js

document.addEventListener("DOMContentLoaded", function(){
    const form = document.getElementById("page-form");
    const editorHolder = document.getElementById("editorjs");
    const bodyJsonInput = document.getElementById("body_json");

    if (!form || !editorHolder || !bodyJsonInput) {
        return;
    }

    let initialData = {
        blocks: []
    };

    const rawBodyJson = bodyJsonInput.value.trim();

    if (rawBodyJson) {
        try {
            const parsedData = JSON.parse(rawBodyJson);

            if (parsedData && Array.isArray(parsedData.blocks)) {
                initialData = parsedData;
            }
        } catch (error) {
            console.error("Editor.js initial data parse error:", error);
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