var work_order_count_info
var work_order_current_page = 0
var work_order_next = null
var work_order_prev = null
var work_order_first_included = true
var work_order_last_included = true
var work_order_total_page = 0
var work_order_pages = []
var work_order_no = ''
var file_upload = true
var empl_on_leave = []
var key = ''
var key2 = ''
var ex_active = 'active'
var ex_closed = null
var ex_all = null
function status(status) {
    if (status == "1") {
        return "Active"
    }
    else if (status == "2") {
        return 'Inactive'
    }
}
$(window).on('load', async function () {

    $(".no-data").hide()
    hideloader();
    if (window.location.pathname == "/list/order") {
        key2 = 'request'
        get_work_order_data(1, 'active', key2)
    }

    if (isNaN(parseInt(location.pathname.split('/')[2])) == false && location.pathname.split('/')[3] == "") {
        $(".clear-tc").hide()
        patch_form(parseInt(location.pathname.split('/')[2]))
    }
//    if (isNaN(parseInt(location.pathname.split('/')[2])) == false && location.pathname.split('/')[3] == "detail") {
//        get_details(parseInt(location.pathname.split('/')[2]))
//    }

    if (window.location.pathname == "/add/order") {
        $(".clear-tc").hide()
        $(".no-data").hide()
    }
});

function create_work_order() {
    if ($("#work_order_form").valid() && file_upload){
        var data = new FormData(document.getElementById('work_order_form'));
        loader();
        $.ajax({
            url: '/api/v1/work_order/',
            type: 'POST',
            data: data,
            processData: false,
            contentType: false,
            success: function (data) {
                hideloader();
                $("#work_order_form")[0].reset();
                $("#emp_id").text(data.work_order_no)
                $("#joning").text(get_date(data.date))
                $('#myModal').modal('toggle');
                $("#tc_file_list").empty()
                $("#tc_file_list").append("Upload CSV files")
            },
            error: function (data) {
                hideloader();
                var i = 0
                for (var key in data.responseJSON) {
                    if (i == 0) {
                        $('.alert-danger').show().delay(1500)
                        $('#error_txt').text(data.responseJSON[key])
                    }
                    i = i + 1
    
                }
            }
        });
    }
}


$(".previous-icon").click(function () { get_work_order_data(work_order_current_page - 1, key, key2); });
$(".next-icon").click(function () { get_work_order_data(work_order_current_page + 1, key, key2); });

function check_work_order(){
    if ($("#order_status").val() == '3' && $("#req_type").val() == '2'){
        $('#myModal').modal('toggle');
    }
    else{
        update_work_order()
    }
}

$("#schedule_service").on('change', function(){
    $("#schedule_service").valid()
})

function submit_order(){
    if ($("#cancel_form").valid()){
        $('#myModal').modal('hide');
        loader();
        data = $("#schedule_service").val()
        update_work_order(data)
    }
}

function update_work_order(args=null) {
    if ($("#work_order_form").valid() && file_upload){
    var data = new FormData(document.getElementById('work_order_form'));
    if (args){
        data.append("schedule_service", args)
    }

    $.ajax({
        url: '/api/v1/work_order/' + parseInt(location.pathname.split('/')[2]) + '/',
        type: 'put',
        data: data,
        //            dataType:'json',
        cache: false,
        processData: false,
        contentType: false,
        success: function (data) {
            hideloader();
            window.setTimeout(function () {
                location.href = '/list/order'
            }, 1000);
            $('.alert-success').show().delay(1500)
            $('#succ-msg').text('Work Order updated successfully.')
        },
        error: function (data) {
            hideloader();
            var i = 0
            for (var key in data.responseJSON) {
                if (i == 0) {
                    $('.alert-danger').show().delay(1500)
                    $('#error_txt').text(data.responseJSON[key])
                }
                i = i + 1

            }
        }
    });
    }
}
function work_order_search(search){
    loader();
    $.ajax({
        url : '/api/v1/work_order/?search='+search.value,
        type : 'get',
        dataType:'json',
        success : function(data) {
            hideloader();
            pagination(data)
            work_order_listtable(data)
        },
        error: function(data) {
            hideloader();
        }
    });
}
$("#closed").on('click', function(){
    ex_active = null
    ex_closed = 'closed'
    ex_all = null
    get_work_order_data(1, 'closed', key2)
});$("#active").on('click', function(){
    ex_active = 'active'
    ex_closed = null
    ex_all = null
    get_work_order_data(1, 'active', key2)
});$("#all").on('click', function(){
    ex_active = null
    ex_closed = null
    ex_all = 'all'
    get_work_order_data(1, 'all', key2)
});

function get_work_order_data(page, args=null, args2=null) {
    key = args
    key2 = args2
    activeclass(key)
    loader();
    $.ajax({
        url: '/api/v1/work_order/?page='+ page +'&'+ key +'=1'+'&'+ key2 +'=1',
        type: 'get',
        dataType: 'json',
        success: function (data) {
            hideloader();
            work_order_listtable(data)
            pagination(data)
        },
        error: function (error) {
            hideloader();
        }
    });
}

function activeclass(){
    if (key === 'closed'){
        var element = document.getElementById("active");
        element.classList.remove("filter-active");
        var element = document.getElementById("closed");
        element.classList.add("filter-active");
        var element = document.getElementById("all");
        element.classList.remove("filter-active");
    }if (key === 'active'){
        var element = document.getElementById("active");
        element.classList.add("filter-active");
        var element = document.getElementById("closed");
        element.classList.remove("filter-active");
        var element = document.getElementById("all");
        element.classList.remove("filter-active");
    }if (key === 'all'){
        var element = document.getElementById("active");
        element.classList.remove("filter-active");
        var element = document.getElementById("closed");
        element.classList.remove("filter-active");
        var element = document.getElementById("all");
        element.classList.add("filter-active");
    }
}


$("#sort-request").on("change", function(){
    if ($(this).val() === '0'){
        key2 = 'request'
    }
    else if($(this).val() === '1'){
        key2 = 'repair'
    }else if($(this).val() === '2'){
        key2 = 'service'
    }
    get_work_order_data(1, key, key2)

});
function pagination(data, ){
    work_order_count_info = data['count']
    work_order_current_page = data['current']
    work_order_next = data['next']
    work_order_prev = data['previous']
    work_order_first_included = true
    work_order_last_included = true
    work_order_total_page = Math.ceil(data['count'] / 8)
    work_order_pages = []

    for (var i = work_order_current_page - 2; i <= work_order_current_page + 2; i++) {
        if (i > 0 && i <= work_order_total_page) {
            work_order_pages.push(i);
        }
    }
    if (work_order_current_page - 2 > 1) {
        work_order_first_included = false
    }
    if (work_order_current_page + 2 < work_order_total_page) {
        work_order_last_included = false
    }
    $(".next-icon-list").empty();
    for (var item of work_order_pages) {
        $(".next-icon-list").append(`<li><a class="element" href="javascript:get_work_order_data(${item}, '${key}', '${key2}');" id="${item}" title="">${item}</a></li>`)
        if (work_order_current_page == item) {
            $("#" + item)[0].parentNode.classList.add("active")
        }
    }
}
function patch_form(id) {
    loader();
    $.ajax({
        url: '/api/v1/work_order/' + id + '/',
        type: 'get',
        dataType: 'json',
        success: function (data) {
            console.log(data)
            hideloader();
            $("input[name='work_order_no']").val(data.work_order_no)
            $("select[name='req_type']").val(data.req_type)
            $("select[name='bus_status']").val(data.bus['status'])
            $("select[name='procedure']").val(data.procedure)
//            $("select[name='bus_system']").val(data.bus_system)
            if (data.order_status == '1'){
                $("#close").hide()
                $("#hold").hide()
            }
            if (data.order_status == '2'){
                $("#open").hide()
            }if (data.order_status == '3'){
                $("#open").hide()
                $("#progress").hide();
                $("#hold").hide();
            }if (data.order_status == '4'){
                $("#open").hide()
                $("#progress").hide()
            }
            $("select[name='order_status']").val(data.order_status)
            $("select[name='employee_assigned']").val(data.employee_assigned)
            $("select[name='bus_system']").val(data.bus['bus_system'])
            patch_employee()
            console.log(data.req_no)
            $("input[name='req_no']").val(data.req_no)
            $("input[name='hourly_rate']").val(data.hourly_rate)
            $("input[name='labor_hours']").val(data.labor_hours)
            $("input[name='bus_id']").val(data.bus['bus_id'])
            $("input[name='no_of_items']").val(data.no_of_items)
            $("input[name='date']").val(get_date(data.assigned_date))
            if (data.completion_date){
                $("input[name='completion_date']").val(get_date(data.completion_date))
            }
            $("textarea[name='supervisor_description']").val(data.supervisor_description)
            $("textarea[name='mechanics_description']").val(data.mechanics_description)

            console.log(data.order_log)
            if (data.order_log.length > 0){
                for (i = 0; i < data.order_log.length; i++) {
                    stri = '<tr><td class="left-content leave-img"><div class="leave-block leave-user"></div><div class="leave-block"><div class="black-txt">'+ data.order_log[i].log +'</div><div class="sub-bold">'+ data.order_log[i].user +'</div></div></td><td class="text-right right-content"><div class="blue-txt">'+ data.order_log[i].date +'</div></td></tr>'
                    $('#order-log').append(stri)
                }
            }
        },
        error: function (error) {
            hideloader();
        }
    });
}



function handle_file_change() {
//    file_upload = true
    if (document.getElementById('items').files.length > 0) {
        $("#tc_file_list").empty()
        $("#tc_file_list").append(document.getElementById('items').files[0].name)
//        $(".clear-tc").show()
        $("#tc_file_list").css("color", "#415c73")
    }
    else {
        $("#tc_file_list").empty()
        $("#tc_file_list").append("Upload Xls, CSV files")
        $("#tc_file_list").css("color", "#97abbc")
    }
}

function work_order_listtable(data) {
    $(".table-block").empty();
    stri = ''
    work_order_item = document.createElement('tr')
    work_order_item.setAttribute('class', 'table-block')
    result_len = (data.results.length)
    $(".empty").empty()
    if (result_len == 0){
        console.log(333333333333333)
        $(".empty").append('<div class="center-txt">No Record Found.</div>')
    }
    else{
        console.log(7777777777777)
        console.log(data)
        for (i = 0; i < result_len; i++) {
            stri = `<tr class="table-block ${data.results[i].id}"><td><div>${data.results[i].work_order_no}</div></td><td>${data.results[i].req_type}</td><td>${data.results[i].req_no}</td><td>${data.results[i].bus_id}</td><td><span class="cus-badge ${bus_class(data.results[i].bus_status)}">${check_status(data.results[i].bus_status)}</span></td><td>${data.results[i].req_by}</td><td>${get_date(data.results[i].assigned_date)}</td><td><span class="cus-badge ${get_class(data.results[i].order_status)} ">${get_status(data.results[i].order_status)}</span></td><td class="actions"><a href="/order/${data.results[i].id}/detail/" onclick="myFunction()" title="View" class="icon-blk green-block"><i class="fas fa-eye"></i></a><a href="/order/${data.results[i].id}/" title="Edit" class="blue-block icon-blk"><i class="fas fa-pen"></i></a></td></tr>`
            document.getElementById('work_order_table').innerHTML = document.getElementById('work_order_table').innerHTML + stri;
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
function bus_class(status){
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
function get_class(status){
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
function get_date(date){
    return  moment(date).format('DD/MM/YYYY');

}

$('#date').on('change', function(){
    $('#date').valid()
});
jQuery.validator.addMethod("numbersonly", function(value, element) {
    return this.optional(element) || /^[0-9]+$/i.test(value);
  }, "Letters only please");


$("#work_order_form").validate({
    errorPlacement: function errorPlacement(error, element) {
        element.after(error);
    },
    errorClass: 'custom-error',
    rules: {
        req_type: {
            required: true,
        },
        procedure: {
            required: true,
        },
        req_no: {
            required: true,
        },
        bus_system: {
            required: true,
        },
        employee_assigned: {
            required: true,
        },hourly_rate: {
            required: true,
            digits: true
        },supervisor_description: {
            required: true,
        },labor_hours: {
            required: true,
            digits: true
        }
    },
    messages: {
        req_type: {
            required: 'Please select the Request Type.',
        },
        procedure: {
            required: 'Please select the Procedure.',
        },
        no_of_items: {
            required: 'Please enter the No. Of Item.',
        },
        req_no: {
            required: 'Please select a Request Number.',
        },
        bus_system: {
            required: "Please select the Bus System.",
        },
        employee_assigned: {
            required: "Please select the Employee Assigned To.",
        },
        hourly_rate: {
            required: "Please select the Hourly Rate.",
            digits: ' Please enter the valid digits.'
        },
        supervisor_description: {
            required: "Please enter the Description.",
        },
        labor_hours: {
            required: "Please enter the Labor Hours.",
            digits: ' Please enter the valid digits.'
        }
    },
});

//function get_details(id) {
//        loader();
//        $.ajax({
//            url: '/api/v1/work_order/' + id + '/',
//            type: 'get',
//            dataType: 'json',
//            success: function (data) {
//                hideloader();
//                total = 0
//                grand = 0
//                if (data.items.length > 0){
//                    for (let i = 0; i < data.items.length; i++) {
//                        price = 0
//                        percent = 0
//                        other = 0
//                        price = data.items[i].quantity * data.items[i].unit_price
//                        percent = (data.items[i].tax / 100) * price
//                        other = data.items[i].other
//
//                        total = price + percent + other
//                        grand = grand + total
//                        const item = data.items[i];
//                        document.getElementById('items').innerHTML = document.getElementById('items').innerHTML + `<tr><td>${i+1}</td><td>${item.description}</td><td>${item.quantity}</td><td>$ ${item.unit_price}</td><td>${item.tax}</td><td>$ ${item.other}</td><td>$ ${total}</td>`
//                    }
//                }
//                else{
//                    $(".blue-head").append('<tr class="text-center"><td colspan="7">No record found</td></tr>')
//                }
////                add_td = ''
////                if (grand > 0){
////                    add_td = `<td colspan="5"></td><th>Total</th><th>$ ${grand}</th>`
////                }
////                document.getElementById('items').innerHTML = document.getElementById('items').innerHTML + `<tr class="borderblue-top"><tr class="blue-head no-border">${add_td}</tr></tr>`
//            },
//            error: function (error) {
//                hideloader();
//            }
//        });
//}

function export_data(email=false, file_type='pdf') {
    if ($("#sort-request").val() != 0){
        var url ='/api/v1/export/work_orders?file_type='+file_type+'&active='+ex_active+'&closed='+ex_closed+'&all='+ex_all+'&request='+$("#sort-request").val()
    }
    else{
        var url ='/api/v1/export/work_orders?file_type='+file_type+'&active='+ex_active+'&closed='+ex_closed+'&all='+ex_all
    }
    if (email) {
        url=url+'&email'
        loader();
        $.ajax({
            url : url,
            type : 'get',
            dataType:'json',
            success : function(data) {
                hideloader();
            },
             error: function(error) {
                 hideloader();
            }
        });
    }
    else {
        window.open(url)
    }
    
}
$('#items').on ('change', function () {
    $(".form-btn-sec").show()

    if (this.files.length > 0) {
        $("#bus_photos1").empty()
            var extension = this.files[0].name.substr( (this.files[0].name.lastIndexOf('.') +1) );
     extension = extension.toLowerCase()

        if (extension != 'csv'){

            $("#bus_photos1").append("Please select Only .csv format file.")
            file_upload = false
        }
        else{
            file_upload = true
        }
        $(".proof").empty()
        $(".proof").append(this.files[0].name)
        $(".proof").css("color", "#415c73")
    }
    else {
        $(".proof").empty();
        $(".proof").append("Select File")
        $(".proof").css("color", "#97abbc")
    }
})

$('#req_type').on('change', function(){

    $("#req_no").empty()
    $("#req_no").append('<option selected disabled hidden>Select Request</option>')

    if ($(this).val() == "1"){
        loader();
        $.ajax({
        url : '/api/v1/pending/repair/',
        type : 'get',
        dataType:'json',
        success : function(data) {
            hideloader();
            if (!data.length > 0){
                $("#req_no").append('<option selected disabled >No Request</option>')
            }
            for(i=0; i<data.length; i++){
                stri = '<option value="'+ data[i].id +'">'+ data[i].repair_no +'</option>'
                $("#req_no").append(stri)
            }
        },
        error: function(data) {
            hideloader();
        }
        });
    }
    if ($(this).val() == "2"){
        loader();
        $.ajax({
        url : '/api/v1/pending/service/',
        type : 'get',
        dataType:'json',
        success : function(data) {
            hideloader();
            if (!data.length > 0){
                $("#req_no").append('<option selected disabled >No Request</option>')
            }
            for(i=0; i<data.length; i++){
            console.log(data[i])
                stri = '<option value="'+ data[i].id +'">'+ data[i].service_no +'</option>'
                $("#req_no").append(stri)
            }
            },
        error: function(data) {
            hideloader();
        }
        });
    }

})

function loader(){
    $('.dynamic-loader').show()
    $('.overlay').show()
}
function hideloader(){
    $('.dynamic-loader').hide()
    $('.overlay').hide()
}

$(function () {
 $("#cancel_form").validate({


    errorPlacement: function errorPlacement(error, element) {
         element.after(error);
    },
    errorClass: 'custom-error',
    rules: {
        schedule_service:{
            required: true,
        }
    },
    messages: {
        schedule_service: {
            required: 'Please select next Schedule Service Date.'
        }
    },

});
});

$("#employee_assigned").on("change", function(){
    patch_employee()
});
function patch_employee(){
    if ($("#employee_assigned").val()){
        $.ajax({
            url: "/api/v1/registration/get_designation/?design="+ $("#employee_assigned").val(),
            type: "get",
            dataType: 'json',
            success: function (data) {
                $("input[name='designation']").val(data)
            }
        });
    }
}
$("#req_no").on("change", function(){
    patch_bus()
});
function patch_bus(){
    console.log($("#req_no").val())
    if ($("#req_no").val()){
        req_type = ''
        if ($("#req_type").val() == '1'){
            req_type = "req_no"
        }
        else{
            req_type = "service_no"
        }

        $.ajax({
            url: "/api/v1/repair/request/get_bus/?"+req_type+"="+ $("#req_no").val(),
            type: "get",
            dataType: 'json',
            success: function (data) {
                console.log(data)
                $("input[name='bus_id']").val(data.bus_id)
                $("select[name='bus_status']").val(data.status)
                $("select[name='bus_system']").val(data.bus_system)
            }
        });

    }
}