jQuery(document).ready(function ($) {
    $('#iox-ai-submit').on('click', function () {
        var question = $('#iox-ai-question').val();

        if (!question) {
            $('#iox-ai-response').html('Please enter a question.');
            return;
        }

        $('#iox-ai-response').html('Thinking...');

        $.ajax({
            url: iox_ai_ajax.ajax_url,
            type: 'POST',
            data: {
                action: 'iox_ai_request',
                question: question
            },
            success: function (response) {
                if (response.success) {
                    $('#iox-ai-response').html(response.data);
                } else {
                    $('#iox-ai-response').html('Error: ' + response.data);
                }
            },
            error: function () {
                $('#iox-ai-response').html('An unexpected error occurred.');
            }
        });
    });
});