i<?php
/*
Plugin Name: Gemini ChatBot
Plugin URI: https://yourwebsite.com/
Description: A WordPress plugin to interact with the Gemini API for a chatbot.
Version: 1.1.0
Author: Your Name
Author URI: https://yourwebsite.com/
License: GPL2
*/

if (!defined('ABSPATH')) {
    exit; // Exit if accessed directly
}

class GeminiChatBot
{
    private $api_key;

    public function __construct()
    {
        $this->api_key = get_option('gemini_api_key'); // Load API key from plugin settings
        add_action('admin_menu', [$this, 'register_admin_menu']);
        add_action('admin_init', [$this, 'register_settings']);
        add_shortcode('gemini_chatbot', [$this, 'render_chatbot']);
        add_action('wp_ajax_gemini_chat', [$this, 'handle_ajax']);
        add_action('wp_ajax_nopriv_gemini_chat', [$this, 'handle_ajax']);
    }

    public function register_admin_menu()
    {
        add_options_page(
            'Gemini ChatBot Settings',
            'Gemini ChatBot',
            'manage_options',
            'gemini-chatbot',
            [$this, 'settings_page']
        );
    }

    public function register_settings()
    {
        register_setting('gemini_chatbot_options', 'gemini_api_key');
    }

    public function settings_page()
    {
        ?>
        <div class="wrap">
            <h1>Gemini ChatBot Settings</h1>
            <form method="post" action="options.php">
                <?php
                settings_fields('gemini_chatbot_options');
                do_settings_sections('gemini_chatbot_options');
                ?>
                <table class="form-table">
                    <tr valign="top">
                        <th scope="row">Gemini API Key</th>
                        <td><input type="text" name="gemini_api_key" value="<?php echo esc_attr(get_option('gemini_api_key')); ?>" class="regular-text" /></td>
                    </tr>
                </table>
                <?php submit_button(); ?>
            </form>
        </div>
        <?php
    }

    public function render_chatbot()
    {
        if (empty($this->api_key)) {
            return '<p>Please configure your Gemini API Key in the settings first.</p>';
        }

        ob_start();
        ?>
        <div id="gemini-chatbot">
            <div id="gemini-messages"></div>
            <input type="text" id="gemini-input" placeholder="Ask me anything..." />
            <button id="gemini-send">Send</button>
        </div>
        <style>
            #gemini-chatbot {
                max-width: 500px;
                margin: 20px auto;
                border: 1px solid #ccc;
                padding: 10px;
                border-radius: 5px;
            }
            #gemini-messages {
                height: 300px;
                overflow-y: scroll;
                margin-bottom: 10px;
            }
            #gemini-input {
                width: calc(100% - 80px);
                padding: 5px;
            }
            #gemini-send {
                width: 60px;
            }
        </style>
        <script>
            document.addEventListener('DOMContentLoaded', function () {
                const chatbot = document.getElementById('gemini-chatbot');
                const messages = document.getElementById('gemini-messages');
                const input = document.getElementById('gemini-input');
                const send = document.getElementById('gemini-send');

                function appendMessage(role, text) {
                    const msg = document.createElement('div');
                    msg.textContent = role + ': ' + text;
                    messages.appendChild(msg);
                    messages.scrollTop = messages.scrollHeight;
                }

                send.addEventListener('click', function () {
                    const question = input.value.trim();
                    if (!question) return;

                    appendMessage('User', question);
                    input.value = '';

                    fetch('<?php echo admin_url('admin-ajax.php'); ?>', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            action: 'gemini_chat',
                            question: question,
                            security: '<?php echo wp_create_nonce('gemini_nonce'); ?>'
                        })
                    })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                appendMessage('Bot', data.data.response);
                            } else {
                                appendMessage('Error', data.data.message || 'An error occurred.');
                            }
                        })
                        .catch(err => appendMessage('Error', 'Could not get a response.'));
                });
            });
        </script>
        <?php
        return ob_get_clean();
    }

    public function handle_ajax()
    {
        check_ajax_referer('gemini_nonce', 'security');

        if (empty($this->api_key)) {
            wp_send_json_error(['message' => 'API key is missing. Please configure the plugin settings.']);
        }

        $question = sanitize_text_field($_POST['question']);
        if (empty($question)) {
            wp_send_json_error(['message' => 'Question is required.']);
        }

        $response = $this->send_to_gemini($question);
        if ($response) {
            wp_send_json_success(['response' => $response]);
        } else {
            wp_send_json_error(['message' => 'Failed to fetch response from Gemini API.']);
        }
    }

    private function send_to_gemini($question)
    {
        $url = 'https://api.gemini.google.dev/v1/models/gemini-1.5-flash:generateText';
        $payload = [
            'history' => [
                ['role' => 'user', 'parts' => [$question]]
            ],
            'generation_config' => [
                'temperature' => 0.15,
                'top_p' => 0.1,
                'top_k' => 40,
                'max_output_tokens' => 8192,
                'response_mime_type' => 'text/plain',
            ]
        ];

        $args = [
            'headers' => [
                'Authorization' => 'Bearer ' . $this->api_key,
                'Content-Type' => 'application/json',
            ],
            'body' => wp_json_encode($payload),
            'timeout' => 30,
        ];

        $response = wp_remote_post($url, $args);

        if (is_wp_error($response)) {
            return null; // Network issue or other low-level problem
        }

        $status_code = wp_remote_retrieve_response_code($response);
        if ($status_code !== 200) {
            return null; // API returned an error
        }

        $body = wp_remote_retrieve_body($response);

        try {
            $data = json_decode($body, true, 512, JSON_THROW_ON_ERROR);
        } catch (Exception $e) {
            return null; // JSON decoding failed
        }

        return $data['generations'][0]['text'] ?? 'No response available';
    }
}

new GeminiChatBot();
