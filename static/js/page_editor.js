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
        const rawJson = initialDataElement.textContent.trim();

        if (rawJson) {
            try {
                initialData = JSON.parse(rawJson);
            } catch (error) {
                console.error("Editor.js initial data parse error:", error);
                initialData = {
                    blocks: []
                };
            }
        }
    }

    const editor = new EditorJS({
        holder: "editorjs",
        tools: {
            header: Header,
            list: EditorjsList,

            table: {
                class: Table,
                inlineToolbar: true
            },

            image: {
                class: ImageTool,
                config: {
                    endpoints: {
                        byFile: "/admin/upload/image",
                        byUrl: "/admin/upload/image-by-url"
                    }
                }
            }
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