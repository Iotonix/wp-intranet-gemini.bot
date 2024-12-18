<?php
/*
Plugin Name: IOX AI Basic Plugin
Description: A plugin to send questions to an external AI endpoint via a form and display the response dynamically.
Version: 1.1
Author: aitdev@ait.co.th
*/

// Enqueue JavaScript for AJAX
function iox_ai_enqueue_scripts() {
    wp_enqueue_script('iox-ai-script', plugin_dir_url(__FILE__) . 'js/iox-ai.js', array('jquery'), null, true);
    wp_localize_script('iox-ai-script', 'iox_ai_ajax', array('ajax_url' => admin_url('admin-ajax.php')));
}
add_action('wp_enqueue_scripts', 'iox_ai_enqueue_scripts');

// Register a widget shortcode
function iox_ai_widget_form() {
    ob_start();
    ?>
    <div id="iox-ai-widget">
        <h3>Ask the IOX AI Agent</h3>
        <textarea id="iox-ai-history" style="width: 100%; height: 150px; margin-bottom: 10px;" readonly></textarea>
        <input type="text" id="iox-ai-question" placeholder="Type your question here..." style="width: 100%; padding: 8px; margin-bottom: 10px;">
        <button id="iox-ai-submit" style="padding: 8px 16px; cursor: pointer;">Ask</button>
        <div id="iox-ai-response" style="margin-top: 15px; white-space: pre-wrap;"></div>
    </div>
    <?php
    return ob_get_clean();
}
add_shortcode('iox_ai_widget', 'iox_ai_widget_form');

// AJAX handler for the question
function iox_ai_handle_ajax_request() {
    $question = sanitize_text_field($_POST['question']);
    $url = 'http://172.25.201.55:5000/gcits/query';

    $response = wp_remote_post($url, array(
        'body'    => json_encode(array('question' => $question)),
        'headers' => array('Content-Type' => 'application/json'),
        'timeout' => 60,
    ));

    if (is_wp_error($response)) {
        wp_send_json_error('Error connecting to the AI server.');
    } else {
        $body = wp_remote_retrieve_body($response);
        $decoded = json_decode($body, true);

        // Return only the clean response text
        if (isset($decoded['response'])) {
            $clean_response = trim($decoded['response']); // Remove any trailing spaces/newlines
            wp_send_json_success($clean_response);
        } else {
            wp_send_json_error('Invalid response format from AI server.');
        }
    }
}

add_action('wp_ajax_iox_ai_request', 'iox_ai_handle_ajax_request');
add_action('wp_ajax_nopriv_iox_ai_request', 'iox_ai_handle_ajax_request');
