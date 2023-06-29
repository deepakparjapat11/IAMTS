var a = NaN
var active = null
var completed = null
var all = null
var check = true
$("#service_request_form").validate({
    errorPlacement: function errorPlacement(error, element) {
         element.after(error);
    },
    errorClass: 'custom-error',
    rules: {
        bus: {
            required: true,
            remote: {
                url: "/api/v1/service/request/check_request/",
                type: "get",
                data: {
                    'bus_id': function(){
                        return $('#bus_id').val();
                    }
                }
                }
        },
        resolution_date: {
            required: true,
        },
        description: {
            required: true,
        },
        user: {
            required: true,
        },
        bus_system: {
            required: true,
        }
    },
        messages: {
        bus: {
            required: 'Please enter Bus Id. ',
            remote: 'Service/Repair Request is already in the queue.'
        },
        resolution_date: {
            required: ' Please select resolution date.',
        },
        description: {
            required: 'Please enter Description.',
        },
        user: {
            required: 'Please select request assign to.',
        },
        bus_system: {
            required: 'Please select Bus System',
        },
    },
});
//function get_date(date){
//    var myDate = new Date(date);
//    return `${myDate.getMonth() + 1}/${myDate.getDate()}/${myDate.getFullYear()}`
//
//}
function submit_form(){
    if ($("#service_request_form").valid()){
        var values = {};
        $.each($('#service_request_form').serializeArray(), function(i, field) {
            values[field.name] = field.value;
        });

        loader();
        $.ajax({
            url : '/api/v1/service/request/',
            type : 'POST',
            data : values,
            dataType:'json',
            success : function(data) {
                hideloader();
//            window.setTimeout(function(){
//                location.href = '/list/service'
//            }, 2000);
//
//            $('.alert-success').show().delay(1500)
//            $('#succ-msg').text('Request added successfully.')
             $("#service_request_form")[0].reset();
                $("#emp_id").text(data.service_no)
                $("#joning").text(get_date(data.resolution_date))
                $('#myModal').modal('toggle');
            },
            error: function (data) {
                hideloader();
                var i = 0
                for (var key in data.responseJSON) {
                    if (i ==0){
                        $('.alert-danger').show().delay(1500)
                        $('#error_txt').text(`${key} ${data.responseJSON[key][0]}`)
                    }
                    i = i +1
                }
            }
        });
    }
 }

$(window).on('load', function(){
    $(".gridview").hide()
    hideloader();
    if (window.location.pathname == "/list/service"){
        get_service_data(1)
        check = true
    }
     a = parseInt(location.pathname.split('/')[2])
    let b =location.pathname.split('/')[3]
    if (isNaN(a) == false){
    get_service_detail(a, b)
   }
   var url = new URL(window.location.href);
   get_args = url.searchParams.get("bus");
   if (get_args != null){
        $("#bus_id").valid()
   }
   patch_status()

});

function edit_form(){
    if ($("#service_request_form").valid()){
        var values = {};
        $.each($('#service_request_form').serializeArray(), function(i, field) {
            values[field.name] = field.value;
        });
        loader();
        $.ajax({
            url : `/api/v1/service/request/${a}/`,
            type : 'put',
            data : values,
            dataType:'json',
            success : function(data) {
                hideloader();
                window.setTimeout(function(){
                    location.href = '/list/service'
                }, 2000);
                 $('.alert-success').show().delay(1500)
            $('#succ-msg').text('Request edited successfully.')
            },
            error: function(data) {
                hideloader();
                var i = 0
               for (var key in data.responseJSON) {
                   if (i ==0){
                    $('.alert-danger').show().delay(1500)
                    $('#error_txt').text(`${key} ${data.responseJSON[key][0]}`)
                   }
                   i = i +1

                }
            }
        });
    }
 }


$("#bus_id").on("change", function(){
    patch_status()
});
function patch_status(){
    if ($("#bus_id").val()){
        $.ajax({
            url: "/api/v1/repair/request/bus_status/?bus_id="+ $("#bus_id").val(),
            type: "get",
            dataType: 'json',
            success: function (data) {
                $("select[name='bus_status']").val(data)
            }
        });
    }
}

function get_service_detail(id, b) {
    loader();
    $.ajax({
        url: `/api/v1/service/request/${id}/`,
        type: 'get',
        dataType: 'json',
        success: function (data) {
            hideloader();
            if (b != '') {
                patch_details(data)
            }
            else {
                patch_form(data)
            }
        },
        error: function (error) {
            hideloader();
        }
    });
}

function patch_form(data){
    $("input[name='bus']").val(data.bus_id)
    $("input[name='service_no']").val(data.service_no)
    $("input[name='created_at']").val(data.created_at)
    $("input[name='resolution_date']").val(get_date(data.resolution_date))
    $("select[name='bus_status']").val(data.bus_status)
    $("select[name='bus_system']").val(data.bus_system)
    $("input[name='user_name']").val(data.user_name)
    $("textarea[name='description']").val(data.description)
}

function patch_details(data){
     $("#request_id").html(data.service_no)
     $("#created_at").text(get_date(data.created_at))
     $("#resolution_date").text(get_date(data.resolution_date))
     $("#bus_id").text((data.bus_id != '') ? data.bus_id :  'NA' )
     $("#request_status").text(service_status(data.request_status))
     $("#bus_status").text(check_status(data.bus_status))
     $("#user").text(data.user_name)
     $("#bus_system").text((data.bus_system != '' && data.bus_system != null) ? data.bus_system :  'NA' )
     $("#description").text(data.description)
     $("#edit_button").attr("href", '/service/'+data.id+'/')
}
function get_date(date){
    return  moment(date).format('DD/MM/YYYY');
}
var myDate = new Date();

function get_service_data(page){
    active = "active"
    completed = null
    all = null

    var element = document.getElementById("completed");
    element.classList.remove("filter-active");
    var element = document.getElementById("all");
    element.classList.remove("filter-active");
    var element = document.getElementById("active");
    element.classList.add("filter-active");
    loader();
    $.ajax({
        url : `/api/v1/service/request/?page=${page}&active=1`,
        type : 'get',
        dataType:'json',
        success : function(data) {
            hideloader();
            $(".previous-icon").off('click');
            $(".next-icon").off('click');
            var links = document.getElementsByClassName("previous-icon");
            var link = document.getElementsByClassName("next-icon");
            links[0].onclick = function() {
                get_service_data(bus_current_page - 1);
            }
            link[0].onclick = function() {
                get_service_data(bus_current_page + 1);
            }

            if (window.location.pathname == "/list/service"){
                service_listtable(data)
            }
            bus_count_info = data['count']
            bus_current_page = data['current']
            bus_next = data['next']
            bus_prev = data['previous']
            bus_first_included = true
            bus_last_included = true
            bus_total_page = Math.ceil(data['count']/8)
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
                $(".next-icon-list").append(`<li><a class="element" href="javascript:get_service_data(${item});" id="${item}" title="">${item}</a></li>`)
                if (bus_current_page == item){
                    $(`#${item}`)[0].parentNode.classList.add("active")
                }
            }

        },
        error: function(error) {
            hideloader();
        }
    });
}

function get_service_all(page){
    active = null
    completed = null
    all = 'all'
    var element = document.getElementById("completed");
    element.classList.remove("filter-active");
    var element = document.getElementById("active");
    element.classList.remove("filter-active");
    var element = document.getElementById("all");
    element.classList.add("filter-active");
    loader();
    $.ajax({
        url : `/api/v1/service/request/?page=${page}&all=1`,
        type : 'get',
        dataType:'json',
        success : function(data) {
            hideloader();
            $(".previous-icon").off('click');
            $(".next-icon").off('click');
            var links = document.getElementsByClassName("previous-icon");
            var link = document.getElementsByClassName("next-icon");
            links[0].onclick = function() {
                get_service_all(bus_current_page - 1);
            }
            link[0].onclick = function() {
                get_service_all(bus_current_page + 1);
            }

            if (window.location.pathname == "/list/service"){
                service_listtable(data)
            }
            bus_count_info = data['count']
            bus_current_page = data['current']
            bus_next = data['next']
            bus_prev = data['previous']
            bus_first_included = true
            bus_last_included = true
            bus_total_page = Math.ceil(data['count']/8)
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
                $(".next-icon-list").append(`<li><a class="element" href="javascript:get_service_all(${item});" id="${item}" title="">${item}</a></li>`)
                if (bus_current_page == item){
                    $(`#${item}`)[0].parentNode.classList.add("active")
                }
            }

        },
        error: function(error) {
            hideloader();
        }
    });
}

function get_service_completed(page){
    completed = "completed"
    active = null
    all = null
    var element = document.getElementById("active");
    element.classList.remove("filter-active");
    var element = document.getElementById("all");
    element.classList.remove("filter-active");
    var element = document.getElementById("completed");
    element.classList.add("filter-active");
    loader();
    $.ajax({
        url : `/api/v1/service/request/?page=${page}&completed=1`,
        type : 'get',
        dataType:'json',
        success : function(data) {
            hideloader();
            $(".previous-icon").off('click');
            $(".next-icon").off('click');
            var links = document.getElementsByClassName("previous-icon");
            var link = document.getElementsByClassName("next-icon");
            links[0].onclick = function () {
                get_service_completed(bus_current_page - 1);
            }
            link[0].onclick = function() {
                get_service_completed(bus_current_page + 1);
            }

            if (window.location.pathname == "/list/service"){
                service_listtable(data)
            }
            bus_count_info = data['count']
            bus_current_page = data['current']
            bus_next = data['next']
            bus_prev = data['previous']
            bus_first_included = true
            bus_last_included = true
            bus_total_page = Math.ceil(data['count']/8)
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
                $(".next-icon-list").append(`<li><a class="element" href="javascript:get_service_completed(${item});" id="${item}" ">${item}</a></li>`)
                if (bus_current_page == item){
                    $("#"+item)[0].parentNode.classList.add("active")
                }
            }

        },
        error: function(error) {
            hideloader();
        }
    });
}

function pagination(data){

}
$(".previous-icon").click(function(){ get_service_data(bus_current_page - 1); });
$(".next-icon").click(function(){ get_service_data(bus_current_page + 1); });


function service_listtable(data){
    $(".table-block").empty();
    stri = ''
    $(".empty").empty()
    result_len= (data.results.length)
    if (result_len > 0){
        for (i=result_len-1;i>=0;i--){
          stri=`<tr class="table-block"><td ><div class="cus-tooltip"><a href="/detail/${data.results[i].id}/service/">${data.results[i].service_no}</a></td><td>${data.results[i].created_at}</td><td>${data.results[i].resolution_date}</td><td>${data.results[i].bus_id}</td>`
            if (data.results[i].description.length <= 35) {
                stri = `${stri}<td class="elipsis">${data.results[i].description.substring(0, 35)}</td>`
            }
            else{
                stri = `${stri}<td class="elipsis">${data.results[i].description.substring(0, 32)}...</td>`
            }
            stri = `${stri}<td><span class="cus-badge ${service_class(data.results[i].request_status)}">${service_status(data.results[i].request_status)}</span></td><td><span class="cus-badge ${get_class(data.results[i].bus_status)}">${check_status(data.results[i].bus_status)}</span></td><td class="actions"><a href="/detail/${data.results[i].id}/service/" onclick="myFunction()"  title="View" class="icon-blk green-block"><i class="fas fa-eye"></i></a><a href="/service/${data.results[i].id}/"  title="Edit" class="blue-block icon-blk"><i class="fas fa-pen"></i></a></td></tr>`
            $(".header-row").after(stri);
        }
    }
    else{
        $(".empty").append('<div class="center-txt">No Record Found.</div>')
    }
}
function service_class(status){
    if (status == "1"){
        return "red-badge"
    }
    else if(status == "2"){
        return 'green-badge'
    }
    else if(status == "3"){
        return 'blue-badge'
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
function service_status(num){
    if(num == 1){
        return "Pending"
    }if(num == 2){
        return "In progress"
    }if(num == 3){
        return "Resolved"
    }
}
function check_status(num){
    if(num == 1){
        return "IS"
    }if(num == 2){
        return "OOS"
    }if(num == 3){
        return "SS"
    }if(num == 4){
        return "WP"
    }
}

function export_data(email=false, file_type='pdf') {
    var url ='/api/v1/export/service_requests?file_type='+file_type+'&active='+active+'&completed='+completed+'&all='+all
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

function loader(){
    $('.dynamic-loader').show()
    $('.overlay').show()
}
function hideloader(){
    $('.dynamic-loader').hide()
    $('.overlay').hide()
}