function submit_form(){
    if ($("#registration_form").valid()){
        var values = {};
        $.each($('#registration_form').serializeArray(), function(i, field) {
            values[field.name] = field.value;
        });
        loader();
        $.ajax({
            url : '/api/v1/registration/',
            type : 'POST',
            data : values,
            dataType:'json',
            success : function(data) {
                hideloader();
            },
            error: function(error) {
                hideloader();
            }
        });
    }
 }




jQuery.validator.addMethod("lettersonly", function(value, element) {
  return this.optional(element) || /^[a-z]+$/i.test(value);
}, "Letters only please");
jQuery.validator.addMethod("regexs", function(value, element) {
  return this.optional(element) || /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test(value);
}, "not a valid email.");
jQuery.validator.addMethod("regex", function(value, element) {
  return this.optional(element) || /^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,}$/.test(value);
}, "not a valid password.");


$("#registration_form").validate({
    errorPlacement: function errorPlacement(error, element) {
         element.after(error);
    },
    errorClass: 'custom-error',
    rules: {
        first_name: {
            required: true,
            lettersonly: true,
            minlength:1,
            maxlength:30
        },
        last_name: {
            required: true,
            lettersonly: true,
            maxlength:30
        },
        email: {
            required: true,
            maxlength:50,
             regexs: true
        },
        password: {
            required: true,
            minlength: 8,
            maxlength: 20,
            regex: true
        },
        password2: {
            equalTo: '#id_password',
        }
    },
        messages: {
        first_name: {
            required: 'Please enter the first name. ',
            lettersonly: ' Please enter the valid first name. ',
            maxlength: 'First name should be less than equal to 30 characters.'
        },
        last_name: {
            required: 'Please enter the last name.',
            lettersonly: 'Please enter the valid last name.',
            maxlength: 'Last name should be less than equal to 30 characters.'
        },
        email: {
            required: 'Please   enter email address.',
            maxlength: 'Email can have at most 50 characters.',
            regexs: 'Please enter a valid email address.',
        },
        password: {
            required: ' Please enter password.',
            minlength: 'Password should be of at least 8 characters.',
            maxlength: 'Password should be less than equal to 20 characters.',
            regex: 'Password must contains at least one upper case letter, one lower case letter and one digit.'
        },
        password2: {
            required: 'Please confirm your password.',
            equalTo: 'Your password and confirm password do not match.'
        },
    },
});

$("#forgot").validate({
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
    },
    messages: {
    email: {
            required: 'Please enter email address.',
            maxlength: 'Email can have at most 50 characters.',
            regexs: 'Please enter a valid email address.',
        },
    }
});

function loader(){
    $('.dynamic-loader').show()
    $('.overlay').show()
}
function hideloader(){
    $('.dynamic-loader').hide()
    $('.overlay').hide()
}