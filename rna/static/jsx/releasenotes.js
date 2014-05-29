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

var BugLink = React.createClass({
  render: function() {
    if (this.props.bug) {
      return <a href={bugUrl(this.props.bug)}>{this.props.bug}</a>;
    } else {
     return <p></p>;
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

var NoteRow = React.createClass({
  removeNote: function() {
    this.props.removeNote(this.props.note);
  },
  render: function() {
    var note = this.props.note;
    return (
      <tr>
        <td><a href={noteAdminUrl(note.id)}>Edit</a></td>
        <td>{tagOrKnownIssue(note)}</td>
        <td dangerouslySetInnerHTML={{__html: converter.makeHtml(note.note)}} />
        <td><BugLink bug={note.bug} /></td>
        <td>{note.sort_num}</td>
        <td><input type="button" value="Remove" onClick={this.removeNote} /></td>
      </tr>
    );
  }
});

var NoteRows = React.createClass({
  render: function() {
    var noteRows = this.props.data.map(function (note, index) {
      return <NoteRow key={note.id} note={note} removeNote={this.props.removeNote} />;
    }.bind(this));
    return <tbody>{noteRows}</tbody>;
  }
});

var NoteHeader = React.createClass({
  render: function() {
    var headers = this.props.data.map(function (header, index) {
      return <th key={header}>{header}</th>;
    });
    return (
      <thead>
        <tr>{headers}</tr>
      </thead>
    );
  }
});

var NoteTable = React.createClass({
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
      <table>
        <NoteHeader data={headers} />
        <NoteRows data={this.state.data} removeNote={this.removeNote} />
      </table>
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
  <NoteTable url={notesApiUrl} />,
  document.getElementById('note-table')
);
