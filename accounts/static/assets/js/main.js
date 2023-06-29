var most = []
$(window).on('load', function(){
    get_bus_details()
    get_calendar_data()
    get_chart_data()
    if (location.pathname == "/main/dashboard"){
        get_work_order(1)
    }
    if (location.pathname != "/main/dashboard"){
        get_bus_data(1)
    }
//    sort_buses()
});

function get_bus_data(page){
    loader();
    $.ajax({
        url : '/api/v1/list/bus/?page='+page,
        type : 'get',
        dataType:'json',
        success : function(data) {
            pagination(data)
            dashboard_listtable(data)
            hideloader();

        },
        error: function(error) {
            hideloader();
        }
    });
}
function pagination(data){
    bus_count_info = data['count']
    bus_current_page = data['current']
    bus_next = data['next']
    bus_prev = data['previous']
    bus_first_included = true
    bus_last_included = true
    bus_total_page = Math.ceil(data['count']/4)
    bus_pages = []

    for (var i=bus_current_page-2; i<=bus_current_page+2; i++) {
      if(i>0 && i<=bus_total_page){
        bus_pages.push(i);
      }
    }
    if(bus_current_page-2>1){
      bus_first_included=false
    }
    if(bus_current_page+2<bus_total_page){
      bus_last_included=false
    }
    $(".next-icon-list").empty();
    for(var item of bus_pages){
        if (location.pathname == "/main/dashboard"){
            $(".next-icon-list").append('<li><a class="element" href="javascript:get_work_order('+item+');" id="'+item+'" title="">'+(item)+'</a></li>')
        }
        else{
            $(".next-icon-list").append('<li><a class="element" href="javascript:get_bus_data('+item+');" id="'+item+'" title="">'+(item)+'</a></li>')
        }
        if (bus_current_page == item){
            $("#"+item)[0].parentNode.classList.add("active")
        }
    }
}
function dashboard_listtable(data){
    console.log(1111111111)
    console.log(data)
    if (data.count == 0){
        stri = '<div class="center-txt">No Record Found.</div>'
        $(".listbus").append(stri);
    }
    else{
        $(".clear-list").empty();
        stri = ''
        result_len= (data.results.length)
        for (i=result_len-1;i>=0;i--){
          var service = (  data.results[i].schedule_service != '' && data.results[i].schedule_service != null) ?  data.results[i].schedule_service:  'NA'
          var repair = (  data.results[i].schedule_repair != '' && data.results[i].schedule_repair != null) ?  data.results[i].schedule_repair:  'NA'
          stri='<tr class="table-block clear-list"><td><a href="/bus/'+data.results[i].id+'/detail/" class="icon-blk green-block" title="View Detail">'+
                '<i class="fas fa-eye"></i></a><a href="/bus/'+data.results[i].id+'/" class="blue-block icon-blk" title="Edit">'+
                '<i class="fas fa-pen"></i></a></td><td>'+data.results[i].bus_id+'</td><td>'+data.results[i].chassis_number+'</td><td>'+repair+'</td><td class="text-center"><span class="cus-badge '+get_class(data.results[i].status)+'">'+check_status(data.results[i].status)+'</span></td><td>'+service+'</td></tr>'
                $(".listdata").after(stri);
        }
    }
}
function check_status(status){
    if (status == "1"){
        return "IS"
    }
    else if(status == "2"){
        return 'OOS'
    }
    else if(status == "3"){
        return 'SS'
    }
    else if(status == "4"){
        return "WP"
    }
}
function category_class(status){
    if (status == "1"){
        return "Public Transport"
    }
    else if(status == "2"){
        return 'School Transport'
    }
    else if(status == "3"){
        return 'Private Transport'
    }
    else if(status == "4"){
        return "Any other"
    }
}


function get_bus_details() {
    loader();
    $.ajax({
        url: '/api/v1/dashboard/',
        type: 'get',
        dataType: 'json',
        success: function (data) {
            most = data
            sort_buses()
            dashboard(data)
            hideloader();
        },
        error: function (error) {
            hideloader();
        }
    });
}

function get_calendar_data() {
    loader();
    $.ajax({
        url: '/api/v1/bus/calender_data/',
        type: 'get',
        dataType: 'json',
        success: function (data) {
            calendar_render(data)
            hideloader()
        },
        error: function (error) {
            hideloader()
        }
    });
}

function get_chart_data() {
    loader();
    $.ajax({
        url: '/api/v1/bus/bus_data/',
        type: 'get',
        dataType: 'json',
        success: function (data) {
            chart_series_data(data)
            set_label_data(data)
            set_analytics(data)
            hideloader();
        },
        error: function (error) {
            hideloader();
        }
    });
}

$(document).ready(function () {
    $("select").each(function () {
        $('#sorting').val($(this).find('option[selected]').val())
        sort_buses()
    });
    if (location.pathname == "/main/dashboard"){
        $(".previous-icon").click(function(){ get_work_order(bus_current_page - 1); });
        $(".next-icon").click(function(){ get_work_order(bus_current_page + 1); });
    }
    else{
        $(".previous-icon").click(function(){ get_bus_data(bus_current_page - 1); });
        $(".next-icon").click(function(){ get_bus_data(bus_current_page + 1); });
    }
})

$('#sorting').on('change', function(){
    sort_buses()
})
function sort_buses(){
    if ($('#sorting').val() === '1'){
        data = most.sort(function(a,b){return new Date(a.make_year) - new Date(b.make_year)})
        dashboard(data)
    }if ($('#sorting').val() === '2'){
        data = most.sort(function(a,b){return new Date(b.make_year) - new Date(a.make_year)})
        dashboard(data)
    }
}
function dashboard(data){
    console.log(1111111111111)
    $('.grid-width').empty()
    if (data.length == 0){
        stri = '<h3 class="record center-txt">No record found</h3>'
        $('.grid-width').append(stri);
    }
    else{
        $(".grid-width").empty()
        var a = 0
        stri = ''
        $('#last_date').text(data[0].last_modified.date)
        $('#last_time').text(data[0].last_modified.time)
        $('#last_by').text(data[0].last_modified.user)
        for (i=0;i<Math.ceil(data.length/5);i++){
            var stri1 = '', stri2 = '', stri3 = '', stri4 = '', stri5 = '', stri = ''
            if (check(a,data)== true){
                stri1='<div class="grid-box"><div class="cus-tooltip"><a class="detail-btn '+get_class(data[a].status)+'" href="/bus/'+data[a].id+'/detail/" title="View Detail">'+ check_bus_id(data[a].bus_id, data[a].status) +'</a>'+
                '<div class="tooltiptext"><div class="btn-sec"><a '+
                'href=/repair/?bus='+ data[a].id +' class="blue-btn">Add Repair Request</a></div><div class="btn-sec"><a href=/service/?bus=' + data[a].id + ' class="blue-btn">Add Service Request</a></div></div></div></div>'
            }
            if (check(a+1,data)== true){
                stri2 = '<div class="grid-box"><div class="cus-tooltip"><a class="detail-btn '+get_class(data[a+1].status)+'" href="/bus/'+data[a+1].id+'/detail/" title="View Detail">'+ check_bus_id(data[a+1].bus_id, data[a+1].status) +'</a>'+
                '<div class="tooltiptext"><div class="btn-sec"><a '+
                'href=/repair/?bus=' + data[a+1].id + ' class="blue-btn">Add Repair Request</a></div><div class="btn-sec"><a href=/service/?bus=' + data[a+1].id + ' class="blue-btn">Add Service Request</a></div></div></div></div>'
            }
            if (check(a+2,data)== true){
                stri3 ='<div class="grid-box"><div class="cus-tooltip"><a class="detail-btn '+get_class(data[a+2].status)+'" href="/bus/'+data[a+2].id+'/detail/" title="View Detail">'+ check_bus_id(data[a+2].bus_id, data[a+2].status) +'</a>'+
                '<div class="tooltiptext"><div class="btn-sec"><a '+
                'href=/repair/?bus=' + data[a+2].id + ' class="blue-btn">Add Repair Request</a></div><div class="btn-sec"><a href=/service/?bus=' + data[a+2].id + ' class="blue-btn">Add Service Request</a></div></div></div></div>'
            }
            if (check(a+3,data)== true){
                stri4 ='<div class="grid-box"><div class="cus-tooltip"><a class="detail-btn '+get_class(data[a+3].status)+'" href="/bus/'+data[a+3].id+'/detail/" title="View Detail">'+ check_bus_id(data[a+3].bus_id, data[a+3].status) +'</a>'+
                '<div class="tooltiptext"><div class="btn-sec"><a '+
                'href=/repair/?bus=' + data[a+3].id + ' class="blue-btn">Add Repair Request</a></div><div class="btn-sec"><a href=/service/?bus=' + data[a+3].id + ' class="blue-btn">Add Service Request</a></div></div></div></div>'
            }
            if (check(a+4,data)== true){
                stri5 ='<div class="grid-box"><div class="cus-tooltip"><a class="detail-btn '+get_class(data[a+4].status)+'" href="/bus/'+data[a+4].id+'/detail/" title="View Detail">'+ check_bus_id(data[a+4].bus_id, data[a+4].status) +'</a>'+
                '<div class="tooltiptext"><div class="btn-sec"><a '+
                'href=/repair/?bus=' + data[a+4].id + ' class="blue-btn">Add Repair Request</a></div><div class="btn-sec"><a href=/service/?bus=' + data[a+4].id + ' class="blue-btn">Add Service Request</a></div></div></div></div>'
            }
            stri = '<div class="grid-row">'+stri1+stri2+stri3+stri4+stri5+'</div>'
            $(".grid-width").append(stri);
            a = a + 5;
        }
    }

}
function check_bus_id(bus_id, status){
    if (status == "3" ){
        return bus_id+'(SS)'
    }
    else if(status == "4"){
        return bus_id+'(WP)'
    }
    return bus_id
}

function check(index, data){
    if(typeof data[index] === 'undefined') {
        return false;
    }
    else {
        return true
    }
}

function get_class(status){
    if (status == "1"){
        return "green-badge"
    }
    else if(status == "2"){
        return 'red-badge'
    }
    else if(status == "3"){
        return 'green-badge yelow-txt'
    }
    else if(status == "4"){
        return "red-badge"
    }
}

function chart_series_data(data)
{
data = [{y:data.in_service, color: '#90ED7D'}, {y: data.ss , color:'#7CB5EC'}, {y: data.os, color: '#24456e'}]

Highcharts.chart('chart_container', {
title:{
    text:''
},

  chart: {
    type: 'pie',
    animation: false,
    backgroundColor: "#fbfbfb"
  },

  plotOptions: {
    pie: {

      borderWidth: 5,

      dataLabels: {
        enabled: false
      }
    },
    series: {
      states: {
        hover: {
          enabled: false
        }
      }
    }
  },
  tooltip: {
  enabled:false,
  animation: false
  },

  series: [{
    data:data
  }]

});
$('.highcharts-credits').hide()
}
//chart_data = chart_series_data()


if (location.pathname == "/main/dashboard"){
    $(".previous-icon").click(function(){ get_work_order(bus_current_page - 1); });
    $(".next-icon").click(function(){ get_work_order(bus_current_page + 1); });
    }
else{
    $(".previous-icon").click(function(){ get_bus_data(bus_current_page - 1); });
    $(".next-icon").click(function(){ get_bus_data(bus_current_page + 1); });
}


function calendar_render(data){
  var calendarEl = document.getElementById('calendar');
   var event_data = []
   service = data.service_data
   for (i=0; i<service.length; i++){
        urls =  '/list/service?q='+service[i].schedule_service+''
        temp = {start:service[i].schedule_service,description: service[i].bus_no.join(', ') , url: urls, color: "#f6fa0c"}
        event_data.push(temp)
   }
   ser = data.licensing_data
   for (i=0; i<ser.length; i++){
        urls = '/list/bus/?q='+ser[i].vehicle_licensing+''
        temp = {start:ser[i].vehicle_licensing, description: ser[i].bus_no.join(', '), url: urls, color: "#4e97db"}
        event_data.push(temp)
   }

  var calendar = new FullCalendar.Calendar(calendarEl, {
    plugins: [ 'dayGrid' ],
    defaultView: 'dayGridMonth',
    defaultDate:  moment().format('YYYY-MM-DD'),

    eventRender: function(info) {
      var tooltip = new Tooltip(info.el, {
        title: info.event.extendedProps.description,
        placement: 'top',
        trigger: 'hover',
        container: 'body'
      });
    },

    events: event_data
  });

  calendar.render();

}

function set_label_data(data){
$('#is_bus').text(data.in_service)
$('#ss_bus').text(data.ss)
$('#os_bus').text(data.os)
$('#wp_bus').text(data.wp)
$('#tot_is_bus').text(data.in_service + data.ss)
$('#tot_oos_bus').text(data.os + data.wp)
}

function  set_analytics (data){

if (data.last_month > data.this_month){
$('#text2').addClass('green-txt')
$('#text1').addClass('orange-txt')
$('#text1').removeClass('green-txt')
$('#graph_data1').removeClass('greengraph-data')
$('#graph_data2').addClass('greengraph-data')
$('#graph_icon1').removeClass('green-graph-icon').addClass('orange-graph-icon')
$('#graph_icon2').addClass('green-graph-icon').removeClass('orange-graph-icon')
$('#arrow1').removeClass('green-arow').addClass('orange-arow')
$('#arrow2').addClass('green-arow')

}
}

function loader(){
    $('.dynamic-loader').show()
    $('.overlay').show()
}
function hideloader(){
    $('.dynamic-loader').hide()
    $('.overlay').hide()
}

function get_work_order(page){
    loader();
    $.ajax({
        url: '/api/v1/dashboard/order/?page='+page,
        type: 'get',
        dataType: 'json',
        success: function (data) {
            pagination(data)
            work_order_listtable(data)
            hideloader();

        },
        error: function (error) {
            hideloader();
        }
    });
}

function work_order_listtable(data) {
    $(".remove-cls").empty();
    stri = ''
    work_order_item = document.createElement('tr')
    work_order_item.setAttribute('class', 'remove-cls')
    result_len = data.results.length
    $("#no-data").empty()
    if (result_len == 0){
        $("#no-data").append('<div class="center-txt">No Record Found.</div>')
    }
    else{
        for (i = 0; i < result_len; i++) {
            stri = '<tr class="table-block remove-cls '+ data.results[i].id +'"><td><div>'+ data.results[i].work_order_no +'</div></td><td>'+ data.results[i].req_type +'</td><td>'+data.results[i].req_no +'</td><td>'+ data.results[i].req_by +'</td><td>'+ get_date(data.results[i].date)+'</td><td><span class="cus-badge '+ get_order_class(data.results[i].order_status)+'">'+ get_status(data.results[i].order_status) +'</span></td><td class="actions"><a href="/order/'+data.results[i].id+'/detail/" onclick="myFunction()" title="View" class="icon-blk green-block"><i class="fas fa-eye"></i></a><a href="/order/'+data.results[i].id+'/" title="Edit" class="blue-block icon-blk"><i class="fas fa-pen"></i></a></td></tr>'
            $('#work_order_table').append(stri)
        }
    }
}


function get_order_class(status){
    if (status == '1'){
        return "red-badge"
    }if (status == '2'){
        return "green-badge"
    }if (status == '3'){
        return "blue-badge"
    }if (status == '4'){
        return "yellow-badge"
    }
}
function get_date(date){
    return  moment(date).format('DD/MM/YYYY');
}
function get_status(status){
    if (status == '1'){
        return "Open"
    }if (status == '2'){
        return "In Progress"
    }if (status == '3'){
        return "Closed"
    }if (status == '4'){
        return "Hold"
    }
}