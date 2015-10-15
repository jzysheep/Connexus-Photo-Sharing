/**
 * Created by Fuzhou Zou on 10/9/15.
 */

$(document).ready(function(){
    Dropzone.options.myDropZone = {
        addRemoveLinks: true,
        uploadMultiple: false,
        autoProcessQueue: false,
        parallelUploads: 6,
        maxFiles: 6,

        init:function() {
            myDropzone = this;

            $('#upload_img').on('click', function(e){
                e.preventDefault();
                e.stopPropagation();
                //num_of_uploads = myDropzone.getQueuedFiles().length
                myDropzone.processQueue();
            });

            //myDropzone.on("processing", function(file) {
            //    var stream_key = location.search.split('stream_key=')[1];
            //    $.ajax({
            //        type: 'POST',
            //        url: '/upload_url_gen',
            //        data: {
            //            stream_key: stream_key
            //        },
            //        dataType: 'json',
            //        success: function (data) {
            //            myDropzone.options.url = data.upload_url;
            //        }
            //    });
            //});

            myDropzone.on('complete', function (file) {
                if (myDropzone.getUploadingFiles().length === 0 && myDropzone.getQueuedFiles().length === 0) {
                    setTimeout(function(){
                        window.location.reload();
                    }, 100);
                }
            });

            myDropzone.on("maxfilesexceeded", function(file) {
                alert("Max Number of Files to upload: 6");
                this.removeFile(file);
            });
        }
    };
});