document.getElementById('updateForm').addEventListener('submit', async (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    const jsonData = JSON.stringify(data);
    const response = await fetch('http://127.0.0.1:8765/maitoy', {
        method: 'put',
        headers: {
            'Content-Type': 'application/json'
        },
        body: jsonData
    });
    const result = await response.json();
    alert(result.message);
});



// 更新滑块值的显示
const sliders = document.querySelectorAll('.slider');
sliders.forEach(slider => {
    const valueDisplay = slider.nextElementSibling;
    valueDisplay.textContent = slider.value;

    slider.addEventListener('input', () => {
        valueDisplay.textContent = parseFloat(slider.value).toFixed(2);
    });
});

// 表单提交事件
document.getElementById('updateForm').addEventListener('submit', function (event) {
    event.preventDefault(); // 阻止表单默认提交行为

    // 获取表单数据
    const formData = new FormData(this);
    const data = {};
    formData.forEach((value, key) => {
        data[key] = value;
    });

    // 打印表单数据到控制台
    console.log('Form Data:', data);

    // 这里可以添加 AJAX 请求或其他逻辑
    alert('表单已提交！');
});