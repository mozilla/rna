/** @jsx React.DOM */

var authToken;
var converter = new Markdown.Converter();
var notesApiUrl = releaseApiUrl + 'notes/';

function authPatch(url, data, callback) {
  function ajaxPatch() {
    $.ajax({
      url: url,
      method: 'POST',
      headers: {
        'Authorization': 'Token ' + authToken,
        'X-HTTP-Method-Override': 'PATCH',
        'Content-Type': 'application/json'
      },
      data: data,
      success: callback
    });
  }

  if (authToken) {
    ajaxPatch();
  } else {
    $.ajax({
      url: '/rna/auth_token/',
      success: function(d) {
        if (d.token) {
          authToken = d.token;
          ajaxPatch();
        }
      }
    });
  }
}

function bugUrl(bug) {
  return 'https://bugzilla.mozilla.org/show_bug.cgi?id=' + bug
}

var BugLink = React.createClass({displayName: 'BugLink',
  render: function() {
    if (this.props.bug) {
      return React.DOM.a( {href:bugUrl(this.props.bug)}, this.props.bug);
    } else {
     return React.DOM.p(null);
    }
  }
});


function noteAdminUrl(noteId) {
    return '/admin/rna/note/' + noteId + '/'
}

function tagOrKnownIssue(note) {
  if(note.is_known_issue && note.is_known_issue != releaseApiUrl) {
    return 'Known issue'
  } else {
    return note.tag
  }
}

var NoteRow = React.createClass({displayName: 'NoteRow',
  removeNote: function() {
    this.props.removeNote(this.props.note);
  },
  render: function() {
    var note = this.props.note;
    return (
      React.DOM.tr(null, 
        React.DOM.td(null, React.DOM.a( {href:noteAdminUrl(note.id)}, "Edit")),
        React.DOM.td(null, tagOrKnownIssue(note)),
        React.DOM.td( {dangerouslySetInnerHTML:{__html: converter.makeHtml(note.note)}} ),
        React.DOM.td(null, BugLink( {bug:note.bug} )),
        React.DOM.td(null, note.sort_num),
        React.DOM.td(null, React.DOM.input( {type:"button", value:"Remove", onClick:this.removeNote} ))
      )
    );
  }
});

var NoteRows = React.createClass({displayName: 'NoteRows',
  render: function() {
    var noteRows = this.props.data.map(function (note, index) {
      return NoteRow( {key:note.id, note:note, removeNote:this.props.removeNote} );
    }.bind(this));
    return React.DOM.tbody(null, noteRows);
  }
});

var NoteHeader = React.createClass({displayName: 'NoteHeader',
  render: function() {
    var headers = this.props.data.map(function (header, index) {
      return React.DOM.th( {key:header}, header);
    });
    return (
      React.DOM.thead(null, 
        React.DOM.tr(null, headers)
      )
    );
  }
});

var NoteTable = React.createClass({displayName: 'NoteTable',
  addNote: function(id) {
    $.ajax({
      url: '/rna/notes/' + id + '/',
      success: function(note) {
        var releases = JSON.stringify({releases: note.releases.concat(releaseApiUrl)})
        authPatch(note.url, releases, function() {
          this.getNotes(); 
        }.bind(this));
      }.bind(this)
    });
  },
  removeNote: function(note) {
    var releases = JSON.stringify({releases: note.releases.filter(function(releaseUrl) {
      return releaseUrl != releaseApiUrl
    })});
    authPatch(note.url, releases, function() {
      this.getNotes(); 
    }.bind(this));
  },
  render: function() {
    var headers = ['Edit', 'Tag/Known issue', 'Note', 'Bug', 'Sort num', 'Remove'];
    return (
      React.DOM.table(null, 
        NoteHeader( {data:headers} ),
        NoteRows( {data:this.state.data, removeNote:this.removeNote} )
      )
    );
  },
  getInitialState: function() {
    return {data: []};
  },
  getNotes: function() {
    $.ajax({
      url: this.props.url,
      success: function(data) {
        this.setState({data: data});
      }.bind(this)
    });
  },
  componentWillMount: function() {
    this.getNotes();

    django_dismissRelatedLookupPopup = window.dismissRelatedLookupPopup;
    window.dismissRelatedLookupPopup = function(win, chosenId) {
      this.addNote(chosenId);
      django_dismissRelatedLookupPopup(win, chosenId);
    }.bind(this)

    django_dismissAddAnotherPopup = window.dismissAddAnotherPopup;
    window.dismissAddAnotherPopup = function(win, newId, newRepr) {
      this.addNote(newId);
      django_dismissAddAnotherPopup(win, newId, newRepr);
    }.bind(this)
  }
});

React.renderComponent(
  NoteTable( {url:notesApiUrl} ),
  document.getElementById('note-table')
);
