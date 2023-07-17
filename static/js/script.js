slouch_position = 0;
function getNotificationPermission(){
   console.log(Notification.permission);
   if (Notification.permission === "granted") {
      console.log("we have permission");
   } else if (Notification.permission !== "denied") {
      Notification.requestPermission().then(permission => {
         console.log(permission);
      });
   }
}

function showNotification(message) {
    console.log("Notification ")
    const notification = new Notification("ALERT!!!", {
       body: `${message}`,
    })
 }

function sendNotification(){
    switch(slouch_position ){
        case 1:
            showNotification("Please correct your posture: UPPER BACK SLOUCH")
            break;
        case 2:
            showNotification("Please correct your posture: LOWER BACK SLOUCH")
            break;
        case 3:
            showNotification("Please correct your posture: RIGHT SLOUCH")
            break;
        case 4:
            showNotification("Please correct your posture: LEFT SLOUCH")
            break;
    }
}

function getColorForSensor(value){
    color = 'rgb('

    step = Math.round(value / 35)
    red = 0;
    green = 0;

    if(step < 9){
        green = (32 * step)
        red = 255;
    }else{
        green = 255;
        red = 255 - (32 * (step % 9+1)) + 1
    }
    if(red >= 256) red = 255;
    if(green >= 256) green = 255;
    if(red <= -1) red= 0;
    if(green <= -1) green = 0;
    color += red;
    color += ","
    color += green;
    color += ',0)'
    return color;
}

function countDigit(num){
    let ans = 0;
    while(num > 0){
        num = Math.floor(num / 10)
        ans ++;
    }
    return ans;
}

function chairDOM(result){
    let sensor_vals = result.data.split(',');
    const sensor1 = document.getElementById('sensor_1');
    const sensor2 = document.getElementById('sensor_2');
    const sensor3 = document.getElementById('sensor_3');
    const sensor4 = document.getElementById('sensor_4');
        
    let sensor1Val = sensor_vals[0];
    let sensor2Val = sensor_vals[1];
    let sensor3Val = sensor_vals[2];
    let sensor4Val = sensor_vals[3];
        
    sensor1.style.backgroundColor = getColorForSensor(sensor1Val);
    sensor2.style.backgroundColor = getColorForSensor(sensor2Val);
    sensor3.style.backgroundColor = getColorForSensor(sensor3Val);
    sensor4.style.backgroundColor = getColorForSensor(sensor4Val);                

    let posture = parseInt(result.prediction);
    const status = document.getElementById('status_value');
    console.log(posture)
    switch (posture){
        case -1:
            status.textContent = "INACTIVE"
            status.style.backgroundColor = "#cccc00";
            break;
        case 0:
            status.textContent = 'NO SLOUCH';
            status.style.backgroundColor = "#7afe87";
            slouch_position = 0;
            break;
        case 1:
            status.textContent = 'UPPER BACK SLOUCH';
            status.style.backgroundColor = "#ba4646";
            slouch_position = 1;            
            break;
        case 2:
            status.textContent = 'LOWER BACK SLOUCH';
            status.style.backgroundColor = "#ba4646";
            slouch_position = 2;            
            break;
        case 3:
            status.textContent = 'RIGHT SLOUCH';
            status.style.backgroundColor = "#ba4646";
            slouch_position = 3;
            break;
        case 4:
            status.textContent = 'LEFT SLOUCH';
            status.style.backgroundColor = "#ba4646";
            slouch_position = 4;
            break;
    }
}

function historyDOM(slouch_count, proper_count){
    var curr_date = new Date(); // for now
    var prev_date = new Date();
    let curr_hour, curr_min, prev_hour, prev_min;
    prev_date.setTime(curr_date.getTime() - 60*1000)    
    
    const historyData = document.getElementById('history_data')
    let data_elem = document.createElement("div")
    data_elem.classList.add("history_data_elem")
    
    if(curr_date.getHours()<10){
        curr_hour = '0' + curr_date.getHours()
    }else{
        curr_hour = '' + curr_date.getHours()
    }

    if(curr_date.getMinutes()<10){
        curr_min = '0' + curr_date.getMinutes()
    }else{
        curr_min = '' + curr_date.getMinutes()
    }

    if(prev_date.getHours()<10){
        prev_hour = '0' + prev_date.getHours()
    }else{
        prev_hour = '' + prev_date.getHours()
    }

    if(prev_date.getMinutes()<10){
        prev_min = '0' + prev_date.getMinutes()
    }else{
        prev_min = '' + prev_date.getMinutes()
    }

    data_elem.innerHTML = `
        <p class="time">${prev_hour}:${prev_min} - ${curr_hour}:${curr_min}</p>
        <p class="slouch_count">${slouch_count}%</p>
        <p class="proper_count">${proper_count}%</p>
        `
    historyData.prepend(data_elem)

}

function chartDOM(slouch_count, proper_count){
    const chartContainer = document.getElementById('chart_container')
    chartContainer.innerHTML = ``
    var chart = anychart.pie();
    var data = [
        {
            x: "slouch", 
            value: slouch_count, 
            normal:{ fill: "#fe7a7a" },
        },
        {
            x: "straight posture", 
            value: proper_count,
            normal:  { fill: "#3ba0ff" },
        },
    ];
  
    chart.data(data);
    chart.background().fill("transparent")
    // chart.normal().fill("aquastyle")
    chart.container('chart_container');    
    chart.draw();
}


$(document).ready(function(){
    function initDOM(){
        loadChairData();
        loadHistoryData();
        loadHistoryData();
        loadHistoryData();
        loadChartData();        
    }

    function loadChairData(){
        req = $.ajax({
            url : '/chairData',
            type: 'GET',
            dataType: 'json',
            success: function(res){                
                chairDOM(res);
            }
        });
    }

    function loadHistoryData(){
        req = $.ajax({
            url : '/historyData',
            type: 'GET',
            dataType: 'json',
            success: function(res){
                historyDOM(parseInt(res.slouch), parseInt(res.proper));
            }
        });
    }
    
    function loadChartData(){
        req = $.ajax({
            url : '/chartData',
            type: 'GET',
            dataType: 'json',
            success: function(res){
                chartDOM(parseInt(res.slouch), parseInt(res.proper));
            }
        });
    }
    
    getNotificationPermission();
    initDOM();
    setInterval(loadChairData, 1500);
    setInterval(loadHistoryData, 60000);
    setInterval(loadChartData, 60000);
    setInterval(sendNotification, 5000);
});