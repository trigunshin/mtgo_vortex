/** BOOKMARK INFO **/

var Bookmark = Backbone.Model.extend();

var BookmarkList = Backbone.Collection.extend ({
    url: "/api/bookmark/",
    model: Bookmark
});

var BookmarkView = Backbone.View.extend({
    tagName: 'li',
    className: 'bookmark',
    events: {
        'click span.delete': 'remove'
    },
    initialize: function(){
        _.bindAll(this, 'render', 'unrender', 'remove');

        this.model.bind('change', this.render);
        this.model.bind('remove', this.unrender);
    },
    render: function(){
        $(this.el).html('<span class="bookmark">' + this.model.get('field') + ' ' +this.model.get('id')+'</span> &nbsp; &nbsp; <span class="delete" style="cursor:pointer; color:red; font-family:sans-serif;">[delete]</span>');
        return this;
    },

    unrender: function(){
        $(this.el).remove();
    },
    remove: function(){
        this.model.destroy();
    }
});

var BookmarkListView = Backbone.View.extend({
    el: $('div#bookmarks'),
    events: {
        'click button#add__bookmark': 'addBookmark',
    },
    initialize: function(){
        _.bindAll(this, 'render', 'addBookmark', 'appendBookmark', 'initialLoad');

        this.collection = new BookmarkList();
        this.collection.bind('add', this.appendBookmark);
        // #AJAX #YOLO #FUCKTHEPOLICE #IHATEBOOTSTRAPTEMPLATES
        this.collection.fetch({success: this.initialLoad});
    },
    initialLoad: function(){
        this.counter = this.collection.length;
        this.render();
    },
    render: function(){
        var self = this;
        $(this.el).append("<button id='add__bookmark'>Add Bookmark</button>");
        $(this.el).append("<ul></ul>");
        _(this.collection.models).each(function(bookmark){
            self.appendBookmark(bookmark);
        }, this);
    },
    addBookmark: function(){
        this.counter++;
        var bookmark = new Bookmark();
        bookmark.set({
            id: this.counter
        });
        this.collection.add(bookmark);
        bookmark.save();
    },
    appendBookmark: function(bookmark) {
        var bookmarkView = new BookmarkView({
            model: bookmark
        });
        $('ul', this.el).append(bookmarkView.render().el);
    }
});

/** GROUP INFO **/

var Group = Backbone.Model.extend();

var GroupList = Backbone.Collection.extend ({
    url: "/api/group/",
    model: Group
});

var GroupView = Backbone.View.extend({
    tagName: 'li',
    className: 'groups',
    events: {
        'click span.delete': 'remove'
    },
    initialize: function(){
        _.bindAll(this, 'render', 'unrender', 'remove');

        this.model.bind('change', this.render);
        this.model.bind('remove', this.unrender);
    },
    render: function(){
        $(this.el).html('<span style="color:black;">' + this.model.get('field') + ' ' +this.model.get('id')+'</span> &nbsp; &nbsp; <span class="delete" style="cursor:pointer; color:red; font-family:sans-serif;">[delete]</span>');
        return this;
    },

    unrender: function(){
        $(this.el).remove();
    },
    remove: function(){
        this.model.destroy();
    }
});

var GroupListView = Backbone.View.extend({
    el: $('div#groups'),
    events: {
        'click button#add__group': 'addGroup',
    },
    initialize: function(){
        _.bindAll(this, 'render', 'addGroup', 'appendGroup', 'initialLoad');

        this.collection = new GroupList();
        this.collection.bind('add', this.appendGroup);
        // #AJAX #YOLO #FUCKTHEPOLICE #IHATEBOOTSTRAPTEMPLATES
        //this.collection.fetch({success: this.initialLoad});
    },
    initialLoad: function(){
        this.counter = this.collection.length;
        this.render();
    },
    render: function(){
        var self = this;
        $(this.el).append("<button id='add__group'>Add Group</button>");
        $(this.el).append("<ul></ul>");
        _(this.collection.models).each(function(group){
            self.appendGroup(group);
        }, this);
    },
    addGroup: function(){
        this.counter++;
        var group = new Group();
        group.set({
            id: this.counter
        });
        this.collection.add(group);
        group.save();
    },
    appendGroup: function(group) {
        var groupView = new GroupView({
            model: group
        });
        $('ul', this.el).append(groupView.render().el);
    }
});

/** USER INFO **/

var User = Backbone.Model.extend();

var UserList = Backbone.Collection.extend ({
    url: "/api/user/",
    model: User
});

var UserView = Backbone.View.extend({
    tagName: 'li', // name of tag to be created
    className: 'users',
    events: {
        'click span.delete': 'remove'
    },
    initialize: function(){
        _.bindAll(this, 'render', 'unrender', 'remove');

        this.model.bind('change', this.render);
        this.model.bind('remove', this.unrender);
    },
    render: function(){
        $(this.el).html('<span style="color:black;">' + this.model.get('field') + ' ' +this.model.get('id')+'</span> &nbsp; &nbsp; <span class="delete" style="cursor:pointer; color:red; font-family:sans-serif;">[delete]</span>');
        return this;
    },

    unrender: function(){
        $(this.el).remove();
    },
    remove: function(){
        this.model.destroy();
    }
});

var UserListView = Backbone.View.extend({
    el: $('div#users'),
    events: {
        'click button#add__user': 'addUser',
    },
    initialize: function(){
        _.bindAll(this, 'render', 'addUser', 'appendUser', 'initialLoad');

        this.collection = new UserList();
        this.collection.bind('add', this.appendUser);
        // #AJAX #YOLO #FUCKTHEPOLICE #IHATEBOOTSTRAPTEMPLATES
        this.collection.fetch({success: this.initialLoad});
    },
    initialLoad: function(){
        this.counter = this.collection.length;

        this.groups = new GroupListView();
        this.groups.parentView = this;
        $(this.el).append(this.groups.el);

        this.render();
    },
    render: function(){
        var self = this;
        $(this.el).append("<button id='add__user'>Add User</button>");
        $(this.el).append("<ul></ul>");
        _(this.collection.models).each(function(user){
            self.appendUser(user);
        }, this);
    },
    addUser: function(){
        this.counter++;
        var user = new User();
        user.set({
            id: this.counter
        });
        this.collection.add(user);
        user.save();
    },
    appendUser: function(user) {
        var userView = new UserView({
            model: user
        });
        $('ul', this.el).append(userView.render().el);
    }
});



var userListView = new UserListView();
var groupListView = new GroupListView();
var bookmarkListView = new BookmarkListView();
/*
var user = new User({'name': 'John Doyle'});
users.add(user);

var user = new User({id: 1}) //Create an instance initializing the object ID you want to recover
users.add(user) //Add the instance to the collection to know the url based backbone of the collection
user.fetch ({ // generate GET /users/1
    success: function () {
        // {print “id”: 1, “name”: “John”, “surname”: “Doyle”}
        alert(JSON.stringify(user.attributes))
    }
});
*/