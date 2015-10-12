/**
 * Created by Fuzhou Zou on 10/9/15.
 */

$(document).ready(function(){
    Dropzone.options.myDropZone = {
        addRemoveLinks: true,
        autoProcessQueue: false,
        parallelUploads: 6,
        maxFiles: 6,

        init: function() {
            myDropzone = this;

            $('#upload_img').on('click', function(e){
                e.preventDefault();
                e.stopPropagation();
                //num_of_uploads = myDropzone.getQueuedFiles().length
                myDropzone.processQueue();
            })

            myDropzone.on('complete', function (file) {
                if (myDropzone.getUploadingFiles().length === 0 && myDropzone.getQueuedFiles().length === 0) {
                    setTimeout(function(){
                        window.location.reload();
                    }, 100);
                }
            });

            myDropzone.on("maxfilesexceeded", function(file) {
                console.log("Max Number of Files!");
                this.removeFile(file);
            });
        }
    };
});
