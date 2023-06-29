jQuery.validator.addMethod("regexs", function(value, element) {
  return this.optional(element) || /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test(value);
}, "not a valid email.");
jQuery.validator.addMethod("regex", function(value, element) {
  return this.optional(element) || /^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,}$/.test(value);
}, "not a valid password.");

$("#login_form").validate({
    errorPlacement: function errorPlacement(error, element) {
         element.after(error);
    },
    errorClass: 'custom-error',
    rules: {
        email: {
            required: true,
            maxlength:50,
             regexs: true
        },
        password: {
            required: true,
        }
    },
    messages: {
        email: {
            required: 'Please enter email address.',
            maxlength: 'Email can have at most 50 characters.',
            regexs: 'Please enter a valid email address.',
        },
        password: {
            required: ' Please enter password.',
        }
    }
});

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