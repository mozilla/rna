var authToken;
var converter = new Markdown.Converter();
var noteKeys = ['id', 'tag', 'is_known_issue', 'note', 'bug', 'sort_num'];
var noteTable = d3.select('#note-table');
var notesApiUrl = releaseApiUrl + 'notes/';


function editLink(id) {
    //TODO: make this a popup with a callback to updateNoteTable
    return '<a href="/admin/rna/note/' + id + '/">Edit</a>'
}


function bugLink(bug) {
    if (bug) {
        return '<a href="https://bugzilla.mozilla.org/show_bug.cgi?id=' + bug + '">' + bug + '</a>';
    }
}


function removeButton(id) {
    return '<input type="button" name="remove-note-' + id + '" value="Remove"></input>'
}


function noteValues(note) {
    return [
        editLink(note['id']),
        note['tag'],
        note['is_known_issue'],
        converter.makeHtml(note['note']),
        bugLink(note['bug']),
        note['sort_num'],
        removeButton(note['id'])]
}


function authPatch(url, data, callback) {
    if (authToken) {
        d3.json(url)
            .header('Authorization', 'Token ' + authToken)
            .header('X-HTTP-Method-Override', 'PATCH')
            .header('Content-Type', 'application/json')
            .post(data, callback);
    } else {
        d3.json('/rna/auth_token/', function(d) {
            if (d.token) {
                authToken = d.token
                d3.json(url)
                    .header('Authorization', 'Token ' + authToken)
                    .header('X-HTTP-Method-Override', 'PATCH')
                    .header('Content-Type', 'application/json')
                    .post(data, callback);
            }
        });
    }
}


function addNote(id) {
    d3.json('/rna/notes/' + id + '/', function(note) {
        var releases = JSON.stringify({releases: note.releases.concat(releaseApiUrl)})
        authPatch(note.url, releases, function() {
            d3.json(notesApiUrl, updateNoteTable);
            // TODO: better UI/UX than just adding note to bottom
            let notes = noteTable.selectAll('tr').data().concat(note);
            updateNoteTable(notes);
        });
    });
}

django_dismissRelatedLookupPopup = window.dismissRelatedLookupPopup;
window.dismissRelatedLookupPopup = function(win, chosenId) {
    addNote(chosenId);
    django_dismissRelatedLookupPopup(win, chosenId);
}

django_dismissAddAnotherPopup = window.dismissAddAnotherPopup;
window.dismissAddAnotherPopup = function (win, newId, newRepr) {
    addNote(newId);
    django_dismissAddAnotherPopup(win, newId, newRepr);
}

function removeNote() {
    var note = d3.select(this.name.replace('remove-', '#')).data()[0];
    let newReleases = JSON.stringify(
        {releases: [url for each (url in note.releases) if (url != releaseApiUrl)]});
    authPatch(note.url, newReleases, function() {
        let notes = [n for each (n in noteTable.selectAll('tr').data()) if (n.id != note.id)];
        updateNoteTable(notes);
    });
}

function updateNoteTable(notes) {
    noteTable.selectAll('th')
        .data(['Edit', 'Tag', 'Known issue', 'Note', 'Bug', 'Sort num', 'Remove'])
        .enter().append('th').text(function(d) {return d});

    let noteRowData = noteTable.selectAll('tr').data(notes);
    noteRowData.enter()
        .append('tr').attr('id', function(note) {return "note-" + note.id})
        .selectAll('td')
            .data(noteValues)
            .enter().append('td')
            .html(function(d) {return d})
            .selectAll('input').on('click', removeNote);
    noteRowData.exit().remove()
}

d3.json(notesApiUrl, updateNoteTable);
