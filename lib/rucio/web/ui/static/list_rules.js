/* Copyright European Organization for Nuclear Research (CERN)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * You may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Authors:
 * - Thomas Beermann, <thomas.beermann@cern.ch>, 2014
 */

$(document).ready(function(){
    $('#subbar-details').html('[' + url_param('account') + ', ' + url_param('name') + ', ' + url_param('state') + ', ' + url_param('rse_expression')+ ']');

    $('#loader').html('<b>loading data .... please wait, this may take some time...</b><p>');
    var state = url_param('state');
    if (state.toLowerCase() == 'replicating') {
        state = 'R';
    } else if (state.toLowerCase() == 'ok') {
        state = 'O';
    } else if (state.toLowerCase() == 'stuck') {
        state = 'S';
    } else {
        state = '';
    }
    r.list_account_rules({
        account: url_param('account'),
        activity: url_param('activity'),
        state: state,
        rse_expression: url_param('rse_expression'),
        success: function(data) {
            var download = '<a link="data:application/json;base64,' + btoa(JSON.stringify(data)) + '">download as JSON</a>';
            $('#downloader').html(download);
            $.each(data, function(index, value) {
                value.name = '<a href="/rule?rule_id=' + value.id + '">' + value.name + '</a>';
            });
            
            var dt = $('#resulttable').DataTable( {
                data: data,
                bAutoWidth: false,
                "oLanguage": {
                        "sProcessing": "test..."
                    },
                columns: [{'data': 'name'},
                          {'data': 'rse_expression'},
                          {'data': 'created_at'},
                          {'data': 'state'},
                          {'data': 'locks_ok_cnt'},
                          {'data': 'locks_replicating_cnt'},
                          {'data': 'locks_stuck_cnt'}]
            });
            $('#resulttable_length').find('select').attr('style', 'width: 4em;');
            $('#resulttable_filter').find('input').attr('style', 'width: 10em; display: inline');
            dt.order([0, 'asc']).draw();
            $('#loader').html('');
        },
        error: function(jqXHR, textStatus, errorThrown) {
            if (errorThrown == "Not Found") {
                $('#problem').html("No rules found");
            }
        }
    });
});
