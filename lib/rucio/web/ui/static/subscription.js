/* Copyright European Organization for Nuclear Research (CERN)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * You may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Authors:
 * - Thomas Beermann, <thomas.beermann@cern.ch>, 2014
 * - Mario Lassnig, <mario.lassnig@cern.ch>, 2014
 */

var chosen_account = url_param('account');
var chosen_name = url_param('name')

function create_plot(categories, ok, rep, stuck, sus) {
    $("#history_plot").attr('style', 'height: 40em; width: 60em; margin: 0 auto;');
    var chart_tmp = $("#history_plot").highcharts( {
        plotOptions: { area: { stacking: 'normal' }
                     },
        chart: { type: 'area' },
        yAxis: { title: { text: 'Number of rules' },
                 min: 0
               },
        xAxis: { title: { text: 'Time' },
                 categories: categories.reverse(),
                 labels: {rotation:-45}},
        credits: false,
        title: { text: 'Subscription Rule History' },
        series: []
    });

    var chart = chart_tmp.highcharts();
    chart.addSeries( {
        animation: false,
        name: 'Ok',
        data: ok.reverse(),
        redraw: false,
        color: 'green',
    });
    chart.addSeries( {
        animation: false,
        name: 'Replicating',
        data: rep.reverse(),
        redraw: false,
        color: 'orange',
    });
    chart.addSeries( {
        animation: false,
        name: 'Stuck',
        data: stuck.reverse(),
        redraw: false,
        color: 'red',
    });
    chart.addSeries( {
        animation: false,
        name: 'Suspended',
        data: sus.reverse(),
        redraw: false,
        color: 'black',
    });
}

function create_history(period) {
    var now = new Date();
    var ok = [];
    var rep = [];
    var stuck = [];
    var sus = [];

    var max_j = 6;
    var delta = 10;
    if (period == '1hour') {
        max_j = 6;
        delta = 10;
    } else if (period == '24hours') {
        max_j = 24;
        delta = 60;
    }
    var categories = [];

    for (j = 0; j < max_j; j++) {
        var date = now.getFullYear() + '-' + (now.getMonth() + 1) + '-'
        if (now.getDate() < 10) {
            date += '0' + now.getDate();
        } else {
            date += now.getDate();
        }
        var hour = now.getHours();
        if (hour < 10) {
            hour = '0' + hour;
        }
        var minutes = Math.floor(now.getMinutes() / 10) * 10;

        if (minutes < 10) {
            minutes = '0' + minutes;
        }

        categories.push(hour + ":" + minutes);
        r.list_subscription_rules_state_from_dumps({
            date: date,
            hour: hour,
            minutes: minutes,
            success: function(data) {
                var tmp = [0, 0, 0, 0];
                data = data.split('\n');
                $.each(data, function(index, value) {
                    values = value.split('\t');
                    var acc = values[0];
                    var name = values[1];
                    var state = values[2];
                    var count = parseInt(values[3]);
                    if (acc != chosen_account) {
                        return true;
                    }
                    if (name != chosen_name) {
                        return true;
                    }
                    if (state == 'O') {
                        if (count > 0){
                            tmp[0] = count;
                    }
                    } else if (state == 'R') {
                        if (count > 0){
                            tmp[1] = count;
                        }
                    } else if (state == 'S'){
                        if (count > 0){
                            tmp[2] = count;
                        }
                    } else if (state == 'U'){
                        if (count > 0){
                            tmp[3] = count;
                        }
                    }
                });
                ok.push(tmp[0]);
                rep.push(tmp[1]);
                stuck.push(tmp[2]);
                sus.push(tmp[3]);
                if (j == (max_j - 1)) {
                    create_plot(categories, ok, rep, stuck, sus);
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                if (errorThrown == "Not Found") {
                    $('#problem').html("No data found");
                    $('#loader').html('');
                }
            }
        });
        now.setMinutes(now.getMinutes() - delta);
    }
}

$(document).ready(function(){
    $('#subbar-details').html('[' + url_param('account') + ':' + url_param('name') + ']');

    r.list_subscriptions({'name': url_param('name'),
                'account': url_param('account'),
                             success: function(data) {
                                 if (data == '') {
                                     $('#result').html('Could not find subscription ' + url_param('rule_id'));
                                 } else {
                                     data = data[0];
                                     var sorted_keys = Object.keys(data).sort()
                                     for(var i=0; i<sorted_keys.length; ++i) {
                                         if (data[sorted_keys[i]] != undefined) {
                                             if (typeof data[sorted_keys[i]] === 'boolean'){
                                                 if (data[sorted_keys[i]]) {
                                                     $('#t_metadata').append($('<tr><th>' + sorted_keys[i] + '</th><td style="color: green;">' + data[sorted_keys[i]] + '</td></tr>'));
                                                 } else {
                                                     $('#t_metadata').append($('<tr><th>' + sorted_keys[i] + '</th><td style="color: red;">' + data[sorted_keys[i]] + '</td></tr>'));
                                                 }
                                             } else {
                                                 $('#t_metadata').append($('<tr><th>' + sorted_keys[i] + '</th><td>' + data[sorted_keys[i]] + '</td></tr>'));
                                             }
                                         }
                                     }
                                 }
                                 $("#result").append('<div id="history" class="columns panel"><h4>Rule History</h4><div class="row" style="padding-left: 1em;"><ul class="button-group large-4"><li><div class="button small" id="1hour">1 Hour</div></li><li><div class="button small" id="24hours">24 Hours</div></li>      </ul>    </div>    <div id="history_plot"></div>  </div>')
                                 $("#1hour").click(function(event){ create_history('1hour');});
                                 $("#24hours").click(function(event){ create_history('24hours');});

                             },
                          error: function(jqXHR, textStatus, errorThrown) {
                              $('#result').html('Could not find the rule.');
                          }});
});
