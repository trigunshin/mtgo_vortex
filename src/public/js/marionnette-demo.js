var SignupView = Backbone.Marionette.ItemView.extend({
    template: '#signup-template',
    tagName: 'div',
    className: 'signup-area',
    events: {
        //'click button#signup-submit': 'signup_submit',
        'submit form#submit_form': 'signup_submit'
    },
    ui: {
        emailField:           'input[id=inputEmail]',
        passwordField:        'input[id=inputPassword]',
        passwordConfirmField: 'input[id=inputPassword1]',
        successMessage:      '.msg-success.signup-label',
        authErrorMessage:    '.error-bad-auth.signup-label',
        generalErrorMessage: '.error-unknown.signup-label'
    },
    signup_submit: function(e) {
        e.stopPropagation();
        e.preventDefault();
        var signin_data = {
            'email': this.ui.emailField.val(),
            'password': this.ui.passwordField.val(),
            'password_confirm': this.ui.passwordConfirmField.val()
        };
        MyApp.vent.trigger('signup:submit', signin_data);
    }
});
var ALoginView = Backbone.Marionette.ItemView.extend({
    // Specifies the Underscore.js template to use.
    template:  '#login-template',

    // Properties of the DOM element that will be created/inserted by this view.
    tagName:   'li',
    className: 'login-area dropdown',

    // Shortcut references to components within the UI.
    ui: {
        loginForm:           'form#login',
        emailField:          'input[name=email]',
        passwordField:       'input[name=password]',
        successMessage:      '.msg-success.login-label',
        authErrorMessage:    '.error-bad-auth.login-label',
        generalErrorMessage: '.error-unknown.login-label',
        loggedIn: '#user-hail'
    },
    // Allows us to capture when the user submits the form either via selecting
    // the login button or typing enter in one of the input fields.
    events: {
        'click a#logout': 'logout',
        'submit form#login': 'formSubmitted'
    },
    // Specify the model properties that we should rerender the view on.
    modelEvents: {
        'change:state':        'render',
        'change:stateDetails': 'render'
    },
    logout: function(e) {
        e.stopPropagation();
        e.preventDefault();

        this.model.set({
            email: '',
            password: '',
            action_name: this.model.action_login
        });

        MyApp.vent.trigger('logout:click', this.model);
    },
    formSubmitted: function(event) {
        // Stop the form from actually submitting to the server.
        event.stopPropagation();
        event.preventDefault();

        this.model.set({
            'email': this.ui.emailField.val(),
            'password': this.ui.passwordField.val()
        });

        // Fire off the global event for the controller so that it handles the
        // server communication.
        MyApp.vent.trigger('login:submit', this.model);
    },
    onRender: function() {
        // This is where most of the state-dependent logic goes that used to be
        // written as random jQuery calls. Now, since the view is rerendered on
        // each state change, you just have to modify the DOM relative to the
        // initial content specified in the Underscore template.
        switch (this.model.get('state')) {
            case this.model.notAuthState:
                this.ui.emailField.focus();
                break;
            case this.model.pendingAuthState:
                this.ui.loginForm.find('input, select, textarea').prop('disabled', true);
                this.ui.loginForm.find('input[type=submit]').val('Logging In…');
                break;
            case this.model.authFailState:
                this.ui.authErrorMessage.show();
                this.ui.passwordField.focus();
                break;
            case this.model.authUnknownState:
                this.ui.generalErrorMessage.show();
                break;
            case this.model.authSuccessState:
                //this.ui.successMessage.show();
                this.ui.loggedIn.show();
                this.ui.loginForm.hide();
                // Insert more success logic here.
                // For example, you could reload the page, redirect the user to a
                // different page, or you could fire off a global event that causes
                // the page view to switch to a different one.
        }
    },
    onShow: function() {
        // The browser can't focus on a field that's not displayed on the screen
        // yet. This happens when the view is first shown on the screen.
        if(this.model.notAuthState == this.model.get('state')) {
            this.ui.emailField.focus();
        }
    }
});
var ALoginModel = Backbone.Model.extend({
    defaults:{
        email:     '',
        password:     '',
        state:        this.notAuthState, // This is where you set the initial state.
        stateDetails: '',
        action_name: 'Log in'
    },

    // Define constants to represent the various states and give them descriptive
    // values to help with debugging.
    notAuthState:     'Not Authenticated',
    pendingAuthState: 'Pending Authentication',
    authSuccessState: 'Authentication Success',
    authFailState:    'Authentication Failure',
    authUnknownState: 'Authentication Unknown',

    action_login: 'Log in',
    action_logout: 'Log out',
});

var Vendor = Backbone.Model.extned({
    idAttribute: 'name',
    urlRoot: '/api/vendor/',
    schema: {
        name: 'Text',
    }
});
var Vendors = Backbone.Collection.extend({
    model: Vendor,
    url: '/api/vendor',
});
var VendorView = Backbone.Marionette.ItemView.extend({
    initialize: function() {
        this.listenTo(this.model, 'destroy', this.remove);
    },
    template: '#vendor-template',
    tagName: 'li',
    events: {
        'click input.vendor__clickbox': 'updateVendorPref'
    },
    updateVendorPref: function() {
        var self = this;
        //this.model.doStuff;
    }
});
var VendorsView  = Backbone.Marionette.CollectionView.extend({
    template: "#vendor-list-template",
    itemView: VendorView,
    initialize: function(){}
});
var VendorsLayout = Backbone.Marionette.Layout.extend({
    template: "#vendor-layout-template",
    regions: {
        vendor_list: "#vendor-list"
    }
});

var renderVendorLayout = function(vendor_layout_view) {

};
////////////////////
//// actual app ////
////////////////////

var MyApp = new Backbone.Marionette.Application();
MyApp.addRegions({
    vendor_layout: "#vendor_layout",
    //group_add_modal: "#add_group",
    login_region: "#user_box"
});
MyApp.addInitializer(function(options){
    var signupView = new SignupView();
    MyApp.vent.on("login:success", function(user_model) {
        // TODO manage header bar links with a layout

    });

    MyApp.vent.on("logout:click", function(user_model) {
        //groups.reset();
        //MyApp.group_layout.show(signupView);
        //MyApp.group_add_modal.close();
    });
    MyApp.group_layout.show(signupView);
    $.get('/api/whoami').done(function(data) {
        if(data.email) {
            auth_with_email(data.email);
        }
    }).fail(function(response) {
        //proceed with normal flow
    });
});

var auth_with_email = function(module, email) {
    MyApp.LoginPage.loginModel.set({'email': email});
    return MyApp.LoginPage.loginSuccess({'email': email});
};

// Login page controller.
MyApp.module('LoginPage', function(module, app, backbone, marionette, $, _) {
    var _this = this;
    module.addInitializer(function(options) {
        module.loginModel = new ALoginModel();
        module.loginView = new ALoginView({
            model: module.loginModel
        });
        return app.login_region.show(module.loginView);
    });
    // Called when the async request to the server returns a successful status.
    module.loginSuccess = function(data) {
        module.loginModel.set('action_name', module.loginModel.action_logout);
        app.vent.trigger('login:success', module.loginModel);
        return module.loginModel.set('state', module.loginModel.authSuccessState);
    };

    //TODO module.signupFail; signin header warnings similar to login banners
    module.signupFail = function(response) {
        //TODO handle signup errors
        //TODO link signup into states of login
        // still need to separate the views, but share the model?
    };

    // Called when the async request to the server returns an unsuccessful status.
    module.loginFail = function(response) {
        // HTTP 404 means that the user + password combo was not found.
        // This is the "incorrect email/password" error.
        // Any other status code indicates something unexpected happened on the
        // server such as HTTP 418: I'm a Teapot.
        if (404 === response.status) {
            return module.loginModel.set('state', module.loginModel.authFailState);
        } else {
            module.loginModel.set('state', module.loginModel.authUnknownState);
            return module.loginModel.set('stateDetails', 'Unexpected Server Response: ' + response.status + ' ' + response.statusText);
        }
    };

    app.vent.on('logout:click', function(user_model) {
        $.post('/api/user/logout', {}).done(function(data) {
        }).fail(function(response) {
            // TODO handle error prolly
        });
        return user_model.set('state', user_model.notAuthState);
    });

    app.vent.on('signup:submit', function(signup_model) {
        return $.post('/signup', signup_model).done(function(data) {
            return auth_with_email(data.email);
        }).fail(function(response) {
            return module.loginFail(response);
        });
    });

    // The view fires off a global event when the form is submitted so that this
    // controller can catch it and handle the server communication logic.
    return app.vent.on('login:submit', function(loginModel) {
        loginModel.set('state', loginModel.pendingAuthState);
        return $.post('/api/auth', loginModel.toJSON()).done(function(data) {
            return module.loginSuccess(data);
        }).fail(function(response) {
            return module.loginFail(response);
        });
    });
});

MyApp.start();