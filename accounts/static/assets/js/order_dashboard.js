var order_graph_data = []
var service_graph_data = []

$(window).on('load', async function () {
    get_work_order()
    get_pending_request()
    order_data()

});

function get_pending_request(){
    loader();
    $.ajax({
        url: '/api/v1/pending/service/',
        type: 'get',
        dataType: 'json',
        success: function (data) {
            hideloader();
            service_table(data)
        },
        error: function (error) {
            hideloader();
        }
    });
}

function get_work_order(){
    loader();
    $.ajax({
        url: '/api/v1/list/order/',
        type: 'get',
        dataType: 'json',
        success: function (data) {
            hideloader();
            order_table(data)
        },
        error: function (error) {
            hideloader();
        }
    });
}

function order_table(data){
    if (data.length > 0 ){
        for (i = 0; i < data.length; i++) {
            stri = '<tr><td class="left-content leave-img"><div class="leave-block leave-user">'+
                '<span class="profile-blk"><i class="file-icon"></i></span></div><div class="leave-block">'+
                '<div class="black-txt">Work Order No. - '+ data[i].work_order_no +'</div><div>'+ data[i].req_by +'</div></div></td>'+
                '<td class="text-right right-content"><div class="blue-txt">'+ get_status(data[i].order_status) +'</div><div>'+ get_date(data[i].date) +'</div></td></tr>'
            $('#order').append(stri)
        }
    }
    else{
        $('#order').append('<h3 class="record center-txt">No record found</h3>')
    }


}
function get_status(status){
    if (status == '1'){
        return "Open"
    }if (status == '2'){
        return "In progress"
    }if (status == '4'){
        return "Hold"
    }
}

function get_date(date){
    return  moment(date).format('DD/MM/YYYY');
}

function service_table(data){
    if (data.length > 0){
        for (i = 0; i < data.length; i++) {
            stri = '<tr><td class="left-content leave-img"><div class="leave-block leave-user"><span class="profile-blk">'+
                    '<em class="date-txt">'+ get_day(data[i].created_at) +' <br>'+ get_month(data[i].created_at) +'</em></span></div><div class="leave-block">'+
                    '<div class="black-txt">Req No: '+ data[i].service_no +'</div><div>Bus ID: '+ data[i].bus_id +'</div>'+
                    '</div></td><td class="text-right right-content"><div class="blue-txt">'+ request_status(data[i].request_status) +'</div>'+
                    '<div>'+ data[i].resolution_date +'</div></td></tr>'
            $('#request').append(stri)
        }
    }
    else{
        $('#request').append('<h3 class="record center-txt">No record found</h3>')
    }

}

function get_day(date){
     day = date.split('/')[1]
     return day
}
function get_month(date, format=null){
    if (format){
        const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
        ];
        return monthNames[date]
    }
    else{
        day = date.split('/')[1]
        const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
        ];
        return monthNames[parseInt(day)]
    }
}

function request_status(status){
    if (status == '1'){
        return "Pending"
    }if (status == '2'){
        return "In progress"
    }
}

function order_data(){
    $.ajax({
        url: '/api/v1/graph/order/',
        type: 'get',
        dataType: 'json',
        success: function (data) {
            order_graph_data = data
            order_graph()
        },
        error: function (error) {
        }
    });
    $.ajax({
        url: '/api/v1/graph/service/',
        type: 'get',
        dataType: 'json',
        success: function (data) {
            service_graph_data = data
            service_graph()
        },
        error: function (error) {
        }
    });
}

function change_date(date){
    return new Date(date).getDate() + ' ' + get_month(new Date(date).getMonth(), "format")
}

Chart.plugins.register({
   beforeInit: function(myChart) {
      var data = myChart.data.datasets[0].data;
      var isAllZero = data.reduce((a, b) => a + b) > 0 ? false : true;
      if (!isAllZero) return;
      // when all data values are zero...
      myChart.data.datasets[0].data = data.map((e, i) => i > 0 ? 0 : 1); //add one segment
      myChart.data.datasets[0].backgroundColor = '#d2dee2'; //change bg color
      myChart.data.datasets[0].borderWidth = 0; //no border
      myChart.options.tooltips = false; //disable tooltips
      myChart.options.legend.onClick = null; //disable legend click
   }
});
function order_graph(){
    var ctx = document.getElementById('order-graph').getContext('2d');
    var myChart = new Chart(ctx, {
    type: 'doughnut',
    showTooltips: false,
    onAnimationComplete: function () {

        var ctx = this.chart.ctx;
        ctx.font = this.scale.font;
        ctx.fillStyle = this.scale.textColor
        ctx.textAlign = "center";
        ctx.textBaseline = "bottom";

        this.datasets.forEach(function (dataset) {
            dataset.bars.forEach(function (bar) {
                ctx.fillText(data[0].value + "%", width/2 - 20, width/2, 200);
            });
        })
    },
    data: {
        labels: ['In Progress : '+order_graph_data[0]['progress'], 'Hold : '+ order_graph_data[0]['hold'], 'Closed : '+ order_graph_data[0]['resolve']] ,

        datasets: [{

            data: [order_graph_data[0]['progress'], order_graph_data[0]['hold'], order_graph_data[0]['resolve']],
            backgroundColor: ['rgba(230, 108, 85, 0.8)', 'rgba(69, 184, 83, 0.8)', 'rgba(247, 191, 72, 0.8)', 'rgb(86, 155, 218, 0.8)']
        }]
    },
    options: {
        legend: {
            position: 'bottom',
            labels: {
            fontStyle: "bold",
             fontColor: '#00c9e3'
          },
        },

        tooltips: {
          enabled: true,
          mode: 'nearest',
          callbacks: {
            label: function(tooltipItem, data) {
              var label = data.labels[tooltipItem.index];
              return `${label}`;
            }
          }
        }

    },



    });
}

function service_graph(){
    var ctx = document.getElementById('service-graph').getContext('2d');
    var myChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
        labels: ['Pending : '+ service_graph_data[0]['pending'], 'In Progress : '+service_graph_data[0]['progress'], 'Resolved : '+service_graph_data[0]['resolve']],
        datasets: [{
            data: [service_graph_data[0]['pending'], service_graph_data[0]['progress'], service_graph_data[0]['resolve']],
            backgroundColor: ['rgba(230, 108, 85, 0.8)', 'rgba(69, 184, 83, 0.8)', 'rgb(86, 155, 218, 0.8)']
        }]
    },
    options: {
        legend: {
            position: 'bottom',
            labels: {
            fontStyle: "bold",
             fontColor: '#00c9e3'
          },
        },
        tooltips: {
          enabled: true,
          mode: 'nearest',
          callbacks: {
            label: function(tooltipItem, data) {
              var label = data.labels[tooltipItem.index];
              return `${label}`;
            }
          }
        }
    },
    showTooltips: false,
    onAnimationComplete: function () {

        var ctx = this.chart.ctx;
        ctx.font = this.scale.font;
        ctx.fillStyle = this.scale.textColor
        ctx.textAlign = "center";
        ctx.textBaseline = "bottom";

        this.datasets.forEach(function (dataset) {
            dataset.bars.forEach(function (bar) {
                ctx.fillText(bar.value, bar.x, bar.y - 5);
            });
        })
    }
    });
}

function loader(){
    $('.dynamic-loader').show()
    $('.overlay').show()
}
function hideloader(){
    $('.dynamic-loader').hide()
    $('.overlay').hide()
}