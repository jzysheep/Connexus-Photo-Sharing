/**
 * Created by Fuzhou Zou on 10/9/15.
 */

$(document).ready(function(){
     $( "#slider-range").slider({
         range: true,
         min: 0,
         max: 500,
         values: [75, 300],
         slide: function(event, ui) {
             $('#amount').val("$" + ui.values[ 0 ] + " - $" + ui.values[ 1 ]);
         }
     });
});