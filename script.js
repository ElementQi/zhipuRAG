async function fetchFiles() {
    const response = await fetch('/files');
    const data = await response.json();
    const fileList = document.getElementById('file-list');
    data.files.forEach(file => {
        const label = document.createElement('label');
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = file;
        label.appendChild(checkbox);
        label.appendChild(document.createTextNode(file));
        fileList.appendChild(label);
        fileList.appendChild(document.createElement('br'));
    });
}

async function processFiles() {
    const selectedFiles = [];
    document.querySelectorAll('#file-list input[type="checkbox"]:checked').forEach(checkbox => {
        selectedFiles.push(checkbox.value);
    });
    
    const response = await fetch('/process-files/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(selectedFiles),
    });

    if (response.ok) {

        response.json().then(result => {
            // process all promise message
        
            file_lists = result.processed_files;
            // console.log(file_lists);

            if (file_lists.length == 0){
                alert('缺失index文件');
            } else{
                alert('成功导入' + file_lists);
            }

        })

          
    } else {
        alert('Failed to process files.');
    }
}

document.getElementById('process-btn').addEventListener('click', processFiles);

window.onload = function() {
    fetchFiles();
};


document.getElementById('send-button').addEventListener('click', async () => {
    const inputElement = document.getElementById('dialogue-input');
    const sendButton = document.getElementById('send-button');
    const message = inputElement.value.trim();
    if (message) {
        addMessageToHistory('You', message);
        toggleButtonDisabled(sendButton, true); // 禁用发送按钮
        const response = await sendDialogue(message);
        addMessageToHistory('Model', response.response);
        inputElement.value = ''; // 清空输入框
        toggleButtonDisabled(sendButton, false); // 重新启用发送按钮
    }
});

async function sendDialogue(message) {
    const response = await fetch('/dialogue/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({message}),
    });
    return await response.json();
}

function addMessageToHistory(sender, message) {
    const historyDiv = document.getElementById('dialogue-history');
    const messageDiv = document.createElement('div');
    messageDiv.textContent = `${sender}: ${message}`;
    historyDiv.appendChild(messageDiv);
    historyDiv.scrollTop = historyDiv.scrollHeight; // 滚动到底部
}

function toggleButtonDisabled(button, disabled) {
    button.disabled = disabled;
    button.style.backgroundColor = disabled ? '#aaa' : '#007bff'; // 修改按钮颜色以反映状态
    button.style.cursor = disabled ? 'not-allowed' : 'pointer'; // 修改光标样式
}
