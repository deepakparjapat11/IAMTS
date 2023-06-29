jQuery.validator.addMethod("regex", function(value, element) {
  return this.optional(element) || /^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,}$/.test(value);
}, "not a valid password.");


$("#password_form").validate({
    errorPlacement: function errorPlacement(error, element) {
         element.after(error);
    },
    errorClass: 'custom-error',
    rules: {
        password: {
            required: true,
            minlength: 8,
            maxlength: 20,
            regex: true
        },
        confirm_password: {
            required: true,
            equalTo: '#password',
        }

    },
    messages: {
        password: {
            required: 'Please enter password.',
            minlength: 'Password should be of at least 8 characters.',
            maxlength: 'Password should be less than equal to 20 characters.',
            regex: 'Password must contain at least one upper case letter, one lower case letter and one digit.'
        },
        confirm_password: {
            required: 'Please enter confirm password.',
            equalTo: 'Your password and confirm password do not match.'
        },
    }
});


$('#eye_login1').click(function(){
    if ($('#password').attr('type') == "password"){
            $(this).removeClass();
            $(this).addClass('eye-icon');
            $('#password').prop('type','text');
        }
    else{
        $(this).removeClass();
        $(this).addClass('eye-iconclose');
        $('#password').prop('type','password');
    }
})

$('#eye_login').click(function(){
    if ($('#password1').attr('type') == "password"){
            $(this).removeClass();
            $(this).addClass('eye-icon');
            $('#password1').prop('type','text');
        }
    else{
        $(this).removeClass();
        $(this).addClass('eye-iconclose');
        $('#password1').prop('type','password');
    }
})

function submit_form(){
    let a = location.pathname.split('/')[2]
    let b =location.pathname.split('/')[3]
    if ($("#password_form").valid()){
        var data = $("#password_form")[0]
        var form_data = new FormData(data)
        loader();
        $.ajax({
            url : '/api/v1/password/change_password/'+ a +'/'+ b +'/',
            type : 'POST',
            data : form_data,
//            dataType:'json',
            cache: false,
            processData: false,
            contentType: false,

            success : function(data) {
                hideloader();
                location.href = '/password/success/'
            },
            error: function(data) {
                console.log(data)
                console.log(1111111111111111111)
                $('#error-msge').show().delay(1500)
                $('#error_txt').text("This token has been already used or expire please create new token.")
                window.setTimeout(function(){
                   $('#error-msge').hide()
                }, 2000);
            }
        });
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