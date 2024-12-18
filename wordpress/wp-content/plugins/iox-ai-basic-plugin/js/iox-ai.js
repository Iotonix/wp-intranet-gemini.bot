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
                    var answer = response.data;

                    // Display the current response
                    $('#iox-ai-response').html(answer);

                    // Append the question/answer pair to the history textarea
                    var history = $('#iox-ai-history').val();
                    history += "Q: " + question + "\nA: " + answer + "\n\n";
                    $('#iox-ai-history').val(history);

                    // Clear the input field
                    $('#iox-ai-question').val('');
                } else {
                    $('#iox-ai-response').html('Error: ' + response.data);
                }
            },
            error: function () {
                $('#iox-ai-response').html('An unexpected error occurred.');
            }
        });
    });

    // Trigger message on Enter key press
    $('#iox-ai-question').on('keypress', function (e) {
        if (e.which === 13) { // 13 is the key code for Enter
            e.preventDefault(); // Prevent form submission
            $('#iox-ai-submit').click(); // Trigger the send button click
        }
    });
});
