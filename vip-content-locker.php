<?php
/**
 * Plugin Name: VIP Content Locker
 * Description: Защита контента с Google reCAPTCHA
 * Version: 3.7
 * Author: Manacost Dev
 */

if (!defined('ABSPATH')) exit;

register_activation_hook(__FILE__, 'vip_activate');
function vip_activate() {
    global $wpdb;
    $c = $wpdb->get_charset_collate();
    
    require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
    
    dbDelta("CREATE TABLE IF NOT EXISTS {$wpdb->prefix}vip_code_stats (
        id mediumint(9) NOT NULL AUTO_INCREMENT,
        code_id varchar(255) NOT NULL,
        attempt_type varchar(20) NOT NULL,
        ip_address varchar(100),
        user_agent text,
        attempt_time datetime NOT NULL,
        PRIMARY KEY (id)
    ) $c;");
    
    dbDelta("CREATE TABLE IF NOT EXISTS {$wpdb->prefix}vip_ip_blocks (
        id mediumint(9) NOT NULL AUTO_INCREMENT,
        ip_address varchar(100) NOT NULL,
        blocked_at datetime NOT NULL,
        unblock_at datetime NOT NULL,
        reason text,
        PRIMARY KEY (id),
        UNIQUE KEY ip_address (ip_address)
    ) $c;");
    
    add_option('vip_title', 'Премиум контент');
    add_option('vip_desc', 'Введите код доступа');
    add_option('vip_placeholder', 'Код');
    add_option('vip_btn', 'Открыть');
    add_option('vip_subscribe_note', 'Еще нет доступа? Оформите подписку и получите код.');
    add_option('vip_subscribe_label', 'Оплатить подписку');
    add_option('vip_subscribe_url', '');
    add_option('vip_telegram_url', '');
    add_option('vip_boosty_url', 'https://boosty.to/kolodahearthstone');
    add_option('vip_tribute_url', '');
    add_option('vip_icon', '🔒');
    add_option('vip_captcha_after', '2');
    add_option('vip_block_after', '4');
    add_option('vip_block_duration', '60');
    add_option('vip_access_hours', '12');
    add_option('vip_recaptcha_site', '6LfqywcUAAAAADpaSUTnHMrtJ9S6d6lUdsUvbma0');
    add_option('vip_recaptcha_secret', '6LfqywcUAAAAAAcIr0KqKByw2YzHOR2-rJkrLTvJ');
    add_option('vip_seo_enabled', '1');
    add_option('vip_seo_default_teaser', '');
    add_option('vip_seo_org_name', get_bloginfo('name'));
    add_option('vip_seo_org_logo', '');
    add_option('vip_seo_apply_all', '1');
    add_option('vip_seo_override_plugin', '0');
    add_option('vip_seo_default_og_image', '');
    add_option('vip_seo_twitter_site', '');
    add_option('vip_seo_title_sep', '—');
    add_option('vip_seo_title_format', '%title% %sep% %sitename%');
    add_option('vip_seo_verify_google', '');
    add_option('vip_seo_verify_yandex', '');
    add_option('vip_seo_verify_bing', '');
    add_option('vip_seo_verify_pinterest', '');
    add_option('vip_seo_breadcrumbs', '1');
    add_option('vip_seo_noindex_paged', '1');
    add_option('vip_seo_archive_desc', '');
}

add_action('admin_menu', 'vip_menu');
function vip_menu() {
    add_menu_page('VIP Locker', 'VIP Locker', 'manage_options', 'vip-main', 'vip_settings', 'dashicons-lock');
    add_submenu_page('vip-main', 'Настройки', 'Настройки', 'manage_options', 'vip-main', 'vip_settings');
    add_submenu_page('vip-main', 'Статистика', 'Статистика', 'manage_options', 'vip-stats', 'vip_stats');
    add_submenu_page('vip-main', 'Блокировки', 'Блокировки', 'manage_options', 'vip-blocks', 'vip_blocks');
}

add_action('admin_init', 'vip_register');
function vip_register() {
    register_setting('vip_opts', 'vip_title');
    register_setting('vip_opts', 'vip_desc');
    register_setting('vip_opts', 'vip_placeholder');
    register_setting('vip_opts', 'vip_btn');
    register_setting('vip_opts', 'vip_subscribe_note');
    register_setting('vip_opts', 'vip_subscribe_label');
    register_setting('vip_opts', 'vip_subscribe_url');
    register_setting('vip_opts', 'vip_telegram_url');
    register_setting('vip_opts', 'vip_boosty_url');
    register_setting('vip_opts', 'vip_tribute_url');
    register_setting('vip_opts', 'vip_icon');
    register_setting('vip_opts', 'vip_captcha_after');
    register_setting('vip_opts', 'vip_block_after');
    register_setting('vip_opts', 'vip_block_duration');
    register_setting('vip_opts', 'vip_access_hours');
    register_setting('vip_opts', 'vip_recaptcha_site');
    register_setting('vip_opts', 'vip_recaptcha_secret');
    register_setting('vip_opts', 'vip_seo_enabled');
    register_setting('vip_opts', 'vip_seo_default_teaser');
    register_setting('vip_opts', 'vip_seo_org_name');
    register_setting('vip_opts', 'vip_seo_org_logo');
    register_setting('vip_opts', 'vip_seo_apply_all');
    register_setting('vip_opts', 'vip_seo_override_plugin');
    register_setting('vip_opts', 'vip_seo_default_og_image');
    register_setting('vip_opts', 'vip_seo_twitter_site');
    register_setting('vip_opts', 'vip_seo_title_sep');
    register_setting('vip_opts', 'vip_seo_title_format');
    register_setting('vip_opts', 'vip_seo_verify_google');
    register_setting('vip_opts', 'vip_seo_verify_yandex');
    register_setting('vip_opts', 'vip_seo_verify_bing');
    register_setting('vip_opts', 'vip_seo_verify_pinterest');
    register_setting('vip_opts', 'vip_seo_breadcrumbs');
    register_setting('vip_opts', 'vip_seo_noindex_paged');
    register_setting('vip_opts', 'vip_seo_archive_desc');
}

function vip_settings() {
    ?>
    <div class="wrap">
        <h1>Настройки VIP Locker</h1>
        <form method="post" action="options.php">
            <?php settings_fields('vip_opts'); ?>
            <table class="form-table">
                <tr><th>Заголовок</th><td><input type="text" name="vip_title" value="<?php echo esc_attr(get_option('vip_title')); ?>" class="regular-text"></td></tr>
                <tr><th>Описание</th><td><textarea name="vip_desc" class="large-text"><?php echo esc_textarea(get_option('vip_desc')); ?></textarea></td></tr>
                <tr><th>Сообщение о подписке</th><td><textarea name="vip_subscribe_note" class="large-text" placeholder="Например: Еще нет доступа? Оформите подписку и получите код."><?php echo esc_textarea(get_option('vip_subscribe_note')); ?></textarea><p class="description">Текст подсказки перед кнопкой оплаты.</p></td></tr>
                <tr><th>Placeholder</th><td><input type="text" name="vip_placeholder" value="<?php echo esc_attr(get_option('vip_placeholder')); ?>" class="regular-text"></td></tr>
                <tr><th>Кнопка</th><td><input type="text" name="vip_btn" value="<?php echo esc_attr(get_option('vip_btn')); ?>" class="regular-text"></td></tr>
                <tr><th>Текст кнопки подписки</th><td><input type="text" name="vip_subscribe_label" value="<?php echo esc_attr(get_option('vip_subscribe_label')); ?>" class="regular-text"></td></tr>
                <tr><th>Ссылка на подписку (резервная)</th><td><input type="url" name="vip_subscribe_url" value="<?php echo esc_attr(get_option('vip_subscribe_url')); ?>" class="regular-text" placeholder="https://example.com/pay"><p class="description">Используется, только если ни Telegram, ни Boosty, ни Tribute не указаны.</p></td></tr>
                <tr><th>Telegram (ссылка)</th><td><input type="url" name="vip_telegram_url" value="<?php echo esc_attr(get_option('vip_telegram_url')); ?>" class="regular-text" placeholder="https://t.me/..."></td></tr>
                <tr><th>Boosty (ссылка)</th><td><input type="url" name="vip_boosty_url" value="<?php echo esc_attr(get_option('vip_boosty_url')); ?>" class="regular-text" placeholder="https://boosty.to/..."></td></tr>
                <tr><th>Tribute (ссылка)</th><td><input type="url" name="vip_tribute_url" value="<?php echo esc_attr(get_option('vip_tribute_url')); ?>" class="regular-text" placeholder="https://tribute.tg/..."></td></tr>
                <tr><th>Иконка</th><td><input type="text" name="vip_icon" value="<?php echo esc_attr(get_option('vip_icon')); ?>" class="regular-text"></td></tr>
                <tr><th>Капча после (попыток)</th><td><input type="number" name="vip_captcha_after" value="<?php echo esc_attr(get_option('vip_captcha_after')); ?>" class="small-text"></td></tr>
                <tr><th>Блокировка после</th><td><input type="number" name="vip_block_after" value="<?php echo esc_attr(get_option('vip_block_after')); ?>" class="small-text"></td></tr>
                <tr><th>Блокировка (минут)</th><td><input type="number" name="vip_block_duration" value="<?php echo esc_attr(get_option('vip_block_duration')); ?>" class="small-text"></td></tr>
                <tr><th>Доступ (часов)</th><td><input type="number" name="vip_access_hours" value="<?php echo esc_attr(get_option('vip_access_hours')); ?>" class="small-text"></td></tr>
                <tr><th>reCAPTCHA Site Key</th><td><input type="text" name="vip_recaptcha_site" value="<?php echo esc_attr(get_option('vip_recaptcha_site')); ?>" class="large-text"></td></tr>
                <tr><th>reCAPTCHA Secret Key</th><td><input type="text" name="vip_recaptcha_secret" value="<?php echo esc_attr(get_option('vip_recaptcha_secret')); ?>" class="large-text"></td></tr>
            </table>
            <h2 style="margin-top:30px">SEO</h2>
            <div style="background:#fef3c7;border-left:4px solid #f59e0b;padding:12px 16px;margin:16px 0">
                <b>Замена All in One SEO:</b> включите «Перебивать другие SEO-плагины», затем <b>деактивируйте AIOSEO</b> в Плагины → Установленные. Этот модуль возьмёт на себя title, meta description, keywords, canonical, robots, Open Graph, Twitter Cards и Schema.org для всех записей.
            </div>
            <table class="form-table">
                <tr><th>Включить SEO модуль</th><td><label><input type="checkbox" name="vip_seo_enabled" value="1" <?php checked(get_option('vip_seo_enabled'), '1'); ?>> Эмитить SEO-теги</label></td></tr>
                <tr><th>Применять ко всем записям</th><td><label><input type="checkbox" name="vip_seo_apply_all" value="1" <?php checked(get_option('vip_seo_apply_all'), '1'); ?>> Не только к страницам с шорткодом VIP</label><p class="description">Включите для замены AIOSEO. Иначе SEO-теги добавляются только на закрытые статьи.</p></td></tr>
                <tr><th>Перебивать другие SEO-плагины</th><td><label><input type="checkbox" name="vip_seo_override_plugin" value="1" <?php checked(get_option('vip_seo_override_plugin'), '1'); ?>> Эмитить теги даже если активен Yoast / Rank Math / AIOSEO / SEOPress</label><p class="description" style="color:#b91c1c">⚠ Чтобы не было дублей — деактивируйте AIOSEO после включения этой опции.</p></td></tr>
                <tr><th>Формат заголовка</th><td><input type="text" name="vip_seo_title_format" value="<?php echo esc_attr(get_option('vip_seo_title_format')); ?>" class="regular-text" placeholder="%title% %sep% %sitename%"><p class="description">Доступные плейсхолдеры: <code>%title%</code>, <code>%sitename%</code>, <code>%sep%</code>, <code>%tagline%</code>.</p></td></tr>
                <tr><th>Разделитель</th><td><input type="text" name="vip_seo_title_sep" value="<?php echo esc_attr(get_option('vip_seo_title_sep')); ?>" class="small-text"></td></tr>
                <tr><th>Дефолтный тизер</th><td><textarea name="vip_seo_default_teaser" class="large-text" rows="3" placeholder="Используется если в шорткоде нет атрибута teaser=&quot;...&quot;"><?php echo esc_textarea(get_option('vip_seo_default_teaser')); ?></textarea><p class="description">Фолбэк для meta description когда у записи не заполнены поля «VIP SEO» в редакторе.</p></td></tr>
                <tr><th>OG-картинка по умолчанию</th><td><input type="url" name="vip_seo_default_og_image" value="<?php echo esc_attr(get_option('vip_seo_default_og_image')); ?>" class="large-text" placeholder="https://example.com/share.png"><p class="description">Используется если у записи нет thumbnail и не задана OG-картинка вручную.</p></td></tr>
                <tr><th>Twitter @site</th><td><input type="text" name="vip_seo_twitter_site" value="<?php echo esc_attr(get_option('vip_seo_twitter_site')); ?>" class="regular-text" placeholder="@yourhandle"></td></tr>
                <tr><th>Название организации</th><td><input type="text" name="vip_seo_org_name" value="<?php echo esc_attr(get_option('vip_seo_org_name')); ?>" class="regular-text"></td></tr>
                <tr><th>Логотип (URL)</th><td><input type="url" name="vip_seo_org_logo" value="<?php echo esc_attr(get_option('vip_seo_org_logo')); ?>" class="large-text" placeholder="https://example.com/logo.png"></td></tr>
                <tr><th>Хлебные крошки</th><td><label><input type="checkbox" name="vip_seo_breadcrumbs" value="1" <?php checked(get_option('vip_seo_breadcrumbs'), '1'); ?>> Эмитить BreadcrumbList Schema (Google показывает крошки в выдаче)</label></td></tr>
                <tr><th>noindex для пагинации</th><td><label><input type="checkbox" name="vip_seo_noindex_paged" value="1" <?php checked(get_option('vip_seo_noindex_paged'), '1'); ?>> Закрывать страницы 2+ архивов и пагинации комментариев от индексации</label><p class="description">Уменьшает количество дублей в индексе.</p></td></tr>
                <tr><th>Описание архивов</th><td><textarea name="vip_seo_archive_desc" class="large-text" rows="2" placeholder="Шаблон для категорий/тегов без описания"><?php echo esc_textarea(get_option('vip_seo_archive_desc')); ?></textarea><p class="description">Доступно: <code>%name%</code> (название термина), <code>%sitename%</code>. Если у самого термина задано описание — используется оно.</p></td></tr>
            </table>
            <h3 style="margin-top:24px">Webmaster verification</h3>
            <p class="description">Подтверждение прав в инструментах для вебмастеров. Вставляйте только значение атрибута <code>content</code> из мета-тега, который выдал сервис.</p>
            <table class="form-table">
                <tr><th>Google Search Console</th><td><input type="text" name="vip_seo_verify_google" value="<?php echo esc_attr(get_option('vip_seo_verify_google')); ?>" class="regular-text" placeholder="abc123..."></td></tr>
                <tr><th>Yandex Webmaster</th><td><input type="text" name="vip_seo_verify_yandex" value="<?php echo esc_attr(get_option('vip_seo_verify_yandex')); ?>" class="regular-text" placeholder="abc123..."></td></tr>
                <tr><th>Bing Webmaster</th><td><input type="text" name="vip_seo_verify_bing" value="<?php echo esc_attr(get_option('vip_seo_verify_bing')); ?>" class="regular-text" placeholder="abc123..."></td></tr>
                <tr><th>Pinterest</th><td><input type="text" name="vip_seo_verify_pinterest" value="<?php echo esc_attr(get_option('vip_seo_verify_pinterest')); ?>" class="regular-text" placeholder="abc123..."></td></tr>
            </table>
            <?php submit_button(); ?>
        </form>
    </div>
    <?php
}

function vip_stats() {
    global $wpdb;
    $t = $wpdb->prefix . 'vip_code_stats';
    
    $s = $wpdb->get_var("SELECT COUNT(*) FROM $t WHERE attempt_type='success'") ?: 0;
    $f = $wpdb->get_var("SELECT COUNT(*) FROM $t WHERE attempt_type='failed'") ?: 0;
    $total = $s + $f;
    $rate = $total > 0 ? round(($s / $total) * 100, 1) : 0;
    
    ?>
    <div class="wrap">
        <h1>Статистика</h1>
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:20px;margin:20px 0">
            <div style="background:#dcfce7;padding:20px;border-radius:8px"><h2 style="margin:0;font-size:32px;color:#166534"><?php echo $s; ?></h2><p style="margin:5px 0 0;color:#166534">Успешных</p></div>
            <div style="background:#fee2e2;padding:20px;border-radius:8px"><h2 style="margin:0;font-size:32px;color:#991b1b"><?php echo $f; ?></h2><p style="margin:5px 0 0;color:#991b1b">Неудачных</p></div>
            <div style="background:#dbeafe;padding:20px;border-radius:8px"><h2 style="margin:0;font-size:32px;color:#1e40af"><?php echo $total; ?></h2><p style="margin:5px 0 0;color:#1e40af">Всего</p></div>
            <div style="background:#fef3c7;padding:20px;border-radius:8px"><h2 style="margin:0;font-size:32px;color:#92400e"><?php echo $rate; ?>%</h2><p style="margin:5px 0 0;color:#92400e">Успешность</p></div>
        </div>
        <h2>По кодам</h2>
        <table class="wp-list-table widefat"><thead><tr><th>Код</th><th>Успешно</th><th>Неудачно</th><th>Всего</th></tr></thead><tbody>
        <?php
        $codes = $wpdb->get_results("SELECT code_id, SUM(CASE WHEN attempt_type='success' THEN 1 ELSE 0 END) s, SUM(CASE WHEN attempt_type='failed' THEN 1 ELSE 0 END) f, COUNT(*) total FROM $t GROUP BY code_id ORDER BY total DESC LIMIT 50");
        if ($codes) {
            foreach ($codes as $c) echo "<tr><td><b>{$c->code_id}</b></td><td>{$c->s}</td><td>{$c->f}</td><td>{$c->total}</td></tr>";
        } else {
            echo '<tr><td colspan="4" style="text-align:center">Нет данных</td></tr>';
        }
        ?>
        </tbody></table>
        <h2>Последние попытки</h2>
        <table class="wp-list-table widefat"><thead><tr><th>Время</th><th>Код</th><th>Результат</th><th>IP</th></tr></thead><tbody>
        <?php
        $recent = $wpdb->get_results("SELECT * FROM $t ORDER BY attempt_time DESC LIMIT 20");
        if ($recent) {
            foreach ($recent as $r) {
                $res = $r->attempt_type == 'success' ? '✅' : '❌';
                $time = date('d.m.Y H:i', strtotime($r->attempt_time));
                echo "<tr><td>{$time}</td><td>{$r->code_id}</td><td>{$res}</td><td>{$r->ip_address}</td></tr>";
            }
        } else {
            echo '<tr><td colspan="4" style="text-align:center">Нет данных</td></tr>';
        }
        ?>
        </tbody></table>
    </div>
    <?php
}

function vip_blocks() {
    global $wpdb;
    $t = $wpdb->prefix . 'vip_ip_blocks';
    $wpdb->query("DELETE FROM $t WHERE unblock_at < NOW()");
    $blocks = $wpdb->get_results("SELECT * FROM $t ORDER BY blocked_at DESC");
    ?>
    <div class="wrap">
        <h1>Блокировки IP</h1>
        <div style="background:#fee2e2;padding:20px;border-radius:8px;margin:20px 0"><h2 style="margin:0;font-size:32px;color:#991b1b"><?php echo count($blocks); ?></h2><p style="margin:5px 0 0;color:#991b1b">Активных блокировок</p></div>
        <table class="wp-list-table widefat"><thead><tr><th>IP</th><th>Заблокирован</th><th>Разблокируется</th><th>Причина</th><th>Действия</th></tr></thead><tbody>
        <?php
        if ($blocks) {
            foreach ($blocks as $b) {
                echo "<tr id='ip{$b->id}'><td><b>{$b->ip_address}</b></td><td>" . date('d.m.Y H:i', strtotime($b->blocked_at)) . "</td><td>" . date('d.m.Y H:i', strtotime($b->unblock_at)) . "</td><td>{$b->reason}</td><td><button class='button vip-del' data-id='{$b->id}'>Разблокировать</button></td></tr>";
            }
        } else {
            echo '<tr><td colspan="5" style="text-align:center">Нет блокировок</td></tr>';
        }
        ?>
        </tbody></table>
    </div>
    <script>jQuery(function($){$('.vip-del').click(function(){var id=$(this).data('id');if(!confirm('Разблокировать?'))return;$(this).prop('disabled',true);$.post(ajaxurl,{action:'vip_unblock',id:id,nonce:'<?php echo wp_create_nonce('vu'); ?>'},function(r){if(r.success)$('#ip'+id).fadeOut();else alert('Ошибка');});});});</script>
    <?php
}

add_action('wp_ajax_vip_unblock', 'vip_unblock_ajax');
function vip_unblock_ajax() {
    check_ajax_referer('vu', 'nonce');
    if (!current_user_can('manage_options')) wp_send_json_error();
    global $wpdb;
    $wpdb->delete($wpdb->prefix . 'vip_ip_blocks', ['id' => intval($_POST['id'])]);
    wp_send_json_success();
}

add_action('wp_enqueue_scripts', 'vip_scripts');
function vip_scripts() {
    wp_enqueue_style('vip-css', plugin_dir_url(__FILE__) . 'vip-content-style.css', [], '3.4');
    // FIX: Use time() to force cache clearing on every page load
    wp_enqueue_script('vip-js', plugin_dir_url(__FILE__) . 'vip-content-script.js', ['jquery'], time(), true);
    wp_enqueue_script('recaptcha', 'https://www.google.com/recaptcha/api.js');
    
    wp_localize_script('vip-js', 'vipData', [
        'ajax' => admin_url('admin-ajax.php'),
        'nonce' => wp_create_nonce('vn'),
        'siteKey' => get_option('vip_recaptcha_site')
    ]);
}

add_shortcode('panelVIP', 'vip_shortcode');

function vip_encode_content($content) {
    // Применяем ROT13, затем Base64
    $rot13 = str_rot13($content);
    $base64 = base64_encode($rot13);
    return $base64;
}

function vip_shortcode($atts, $content = null) {
    $a = shortcode_atts([
        'id' => '',
        'teaser' => '',
        'seo_title' => '',
        'seo_desc' => '',
        'keywords' => '',
    ], $atts);
    $id = sanitize_text_field($a['id']);
    if (!$id) return '<p style="color:red">ID не указан</p>';

    vip_seo_register_panel([
        'id' => $id,
        'teaser' => wp_kses_post($a['teaser']),
        'seo_title' => sanitize_text_field($a['seo_title']),
        'seo_desc' => sanitize_text_field($a['seo_desc']),
        'keywords' => sanitize_text_field($a['keywords']),
    ]);
    
    if (vip_is_blocked()) {
        return '<div class="vip-lock-overlay vip-blocked"><div class="vip-lock-content"><div class="vip-lock-icon">🚫</div><h3>Заблокировано</h3><p>Слишком много попыток</p></div></div>';
    }
    
    // Обрабатываем контент и кодируем его для встраивания в HTML
    $processed_content = do_shortcode($content);
    $encoded_content = vip_encode_content($processed_content);
    $content_id_hash = md5($id);
    
    $failed = vip_failed_count();
    $show_cap = $failed >= intval(get_option('vip_captcha_after', 2));
    
    $cap_html = '';
    if ($show_cap) {
        $key = get_option('vip_recaptcha_site');
        $cap_html = "<div class='vip-captcha'><label>Подтвердите что вы не робот:</label><div class='g-recaptcha' data-sitekey='$key'></div></div>";
    }
    
    $warn = '';
    if ($failed > 0) {
        $rem = intval(get_option('vip_block_after', 4)) - $failed;
        $warn = "<div class='vip-warning'>⚠️ Осталось попыток: $rem</div>";
    }
    
    $icon = get_option('vip_icon');
    $title = get_option('vip_title');
    $desc = get_option('vip_desc');
    $ph = get_option('vip_placeholder');
    $btn = get_option('vip_btn');
    $subscribe_note = trim(get_option('vip_subscribe_note', ''));
    $subscribe_label = get_option('vip_subscribe_label', 'Оплатить подписку');
    $subscribe_url = trim(get_option('vip_subscribe_url', ''));
    // Runtime defaults — работают даже если плагин обновлён без реактивации
    $telegram_url = trim(get_option('vip_telegram_url', ''));
    $boosty_raw = get_option('vip_boosty_url', '__vip_default__');
    $boosty_url = ($boosty_raw === '__vip_default__') ? 'https://boosty.to/kolodahearthstone' : trim($boosty_raw);
    $tribute_url = trim(get_option('vip_tribute_url', ''));

    $providers = [];
    if ($telegram_url) $providers[] = ['label' => 'Telegram', 'url' => $telegram_url, 'icon' => '✈'];
    if ($tribute_url)  $providers[] = ['label' => 'Tribute',  'url' => $tribute_url,  'icon' => '◆'];
    if ($boosty_url)   $providers[] = ['label' => 'Boosty',   'url' => $boosty_url,   'icon' => '★'];

    $subscribe_html = '';
    if ($subscribe_note || $providers || $subscribe_url) {
        $subscribe_html .= "<div class='vip-actions'>";
        if ($subscribe_note) {
            $subscribe_html .= "<div class='vip-subscribe-note'>" . nl2br(esc_html($subscribe_note)) . "</div>";
        }
        if ($providers) {
            $subscribe_html .= "<div class='vip-subscribe-dropdown'>";
            $subscribe_html .= "<button type='button' class='vip-subscribe-btn vip-subscribe-toggle' aria-haspopup='true' aria-expanded='false'><span>" . esc_html($subscribe_label) . "</span><span class='vip-subscribe-caret' aria-hidden='true'>▾</span></button>";
            $subscribe_html .= "<ul class='vip-subscribe-menu' role='menu'>";
            foreach ($providers as $p) {
                $subscribe_html .= "<li role='none'><a role='menuitem' href='" . esc_url($p['url']) . "' target='_blank' rel='noopener noreferrer'><span class='vip-provider-icon' aria-hidden='true'>" . esc_html($p['icon']) . "</span><span>" . esc_html($p['label']) . "</span></a></li>";
            }
            $subscribe_html .= "</ul></div>";
        } elseif ($subscribe_url) {
            $subscribe_html .= "<a class='vip-subscribe-btn' href='" . esc_url($subscribe_url) . "' target='_blank' rel='noopener noreferrer'><span>" . esc_html($subscribe_label) . "</span></a>";
        }
        $subscribe_html .= "</div>";
    }
    
    $teaser_html = '';
    $teaser_text = vip_seo_resolve_teaser($a['teaser']);
    if ($teaser_text) {
        $teaser_html = "<div class='vip-public-teaser' itemprop='description'>" . wp_kses_post(wpautop($teaser_text)) . "</div>";
    }

    return "<div class='vip-wrapper' data-id='$id' data-vip-hash='$content_id_hash' itemscope itemtype='https://schema.org/Article'>
        {$teaser_html}
        <div class='vip-lock-overlay' data-vip-paywall='1'>
            <div class='vip-lock-content'>
                <div class='vip-lock-icon'>$icon</div>
                <h3>$title</h3>
                <p>$desc</p>
                $warn
                $cap_html
                <div class='vip-input-group'>
                    <input type='text' class='vip-code' placeholder='$ph'>
                    <button class='vip-btn'>$btn</button>
                </div>
                {$subscribe_html}
                <div class='vip-msg'></div>
            </div>
        </div>
        <script type='text/template' data-vip-id='$content_id_hash'>" . esc_html($encoded_content) . "</script>
    </div>";
}

function vip_is_blocked() {
    global $wpdb;
    $t = $wpdb->prefix . 'vip_ip_blocks';
    $ip = $_SERVER['REMOTE_ADDR'] ?? '';
    $fp = md5($ip . ($_SERVER['HTTP_USER_AGENT'] ?? ''));
    $wpdb->query("DELETE FROM $t WHERE unblock_at < NOW()");
    $blocked = $wpdb->get_var($wpdb->prepare("SELECT COUNT(*) FROM $t WHERE ip_address IN (%s,%s)", $ip, $fp));
    if (isset($_COOKIE['vip_blocked']) && $_COOKIE['vip_blocked'] > time()) return true;
    return $blocked > 0;
}

function vip_failed_count() {
    global $wpdb;
    $t = $wpdb->prefix . 'vip_code_stats';
    $ip = $_SERVER['REMOTE_ADDR'] ?? '';
    $fp = md5($ip . ($_SERVER['HTTP_USER_AGENT'] ?? ''));
    return intval($wpdb->get_var($wpdb->prepare("SELECT COUNT(*) FROM $t WHERE ip_address IN (%s,%s) AND attempt_type='failed' AND attempt_time > DATE_SUB(NOW(), INTERVAL 10 MINUTE)", $ip, $fp)));
}

add_action('wp_ajax_vip_verify', 'vip_verify');
add_action('wp_ajax_nopriv_vip_verify', 'vip_verify');
function vip_verify() {
    check_ajax_referer('vn', 'nonce');
    
    global $wpdb;
    $t = $wpdb->prefix . 'vip_code_stats';
    
    $code = sanitize_text_field($_POST['code'] ?? '');
    $id = sanitize_text_field($_POST['id'] ?? '');
    $recaptcha = sanitize_text_field($_POST['recaptcha'] ?? '');
    $ip = $_SERVER['REMOTE_ADDR'] ?? '';
    $ua = $_SERVER['HTTP_USER_AGENT'] ?? '';
    
    if (vip_is_blocked()) {
        wp_send_json_error(['msg' => 'Заблокировано', 'blocked' => true]);
    }
    
    $failed = vip_failed_count();
    $cap_at = intval(get_option('vip_captcha_after', 2));
    
    // Проверка reCAPTCHA если нужно
    if ($failed >= $cap_at) {
        if (!$recaptcha) {
            wp_send_json_error(['msg' => 'Подтвердите reCAPTCHA', 'show_captcha' => true]);
        }
        
        $secret = get_option('vip_recaptcha_secret');
        $resp = wp_remote_post('https://www.google.com/recaptcha/api/siteverify', [
            'body' => ['secret' => $secret, 'response' => $recaptcha, 'remoteip' => $ip]
        ]);
        
        if (!is_wp_error($resp)) {
            $body = json_decode(wp_remote_retrieve_body($resp), true);
            if (empty($body['success'])) {
                wp_send_json_error(['msg' => 'reCAPTCHA не пройдена. Попробуйте еще раз', 'show_captcha' => true]);
            }
        }
    }
    
    // Проверка кода
    if (strtolower(trim($code)) == strtolower(trim($id))) {
        $hours = intval(get_option('vip_access_hours', 12));
        setcookie('vip_' . md5($id), 'ok', time() + ($hours * 3600), '/');
        
        $wpdb->insert($t, [
            'code_id' => $id,
            'attempt_type' => 'success',
            'ip_address' => $ip,
            'user_agent' => $ua,
            'attempt_time' => current_time('mysql')
        ]);
        
        wp_send_json_success(['msg' => 'Доступ открыт!']);
    } else {
        $wpdb->insert($t, [
            'code_id' => $id,
            'attempt_type' => 'failed',
            'ip_address' => $ip,
            'user_agent' => $ua,
            'attempt_time' => current_time('mysql')
        ]);
        
        $failed++;
        $block_at = intval(get_option('vip_block_after', 4));
        
        if ($failed >= $block_at) {
            $dur = intval(get_option('vip_block_duration', 60));
            $until = time() + ($dur * 60);
            $fp = md5($ip . $ua);
            
            $wpdb->replace($wpdb->prefix . 'vip_ip_blocks', [
                'ip_address' => $ip,
                'blocked_at' => current_time('mysql'),
                'unblock_at' => date('Y-m-d H:i:s', $until),
                'reason' => 'Превышен лимит'
            ]);
            
            $wpdb->replace($wpdb->prefix . 'vip_ip_blocks', [
                'ip_address' => $fp,
                'blocked_at' => current_time('mysql'),
                'unblock_at' => date('Y-m-d H:i:s', $until),
                'reason' => 'Fingerprint'
            ]);
            
            setcookie('vip_blocked', $until, $until, '/');
            wp_send_json_error(['msg' => 'Заблокировано на ' . $dur . ' мин', 'blocked' => true]);
        }
        
        $rem = $block_at - $failed;
        wp_send_json_error(['msg' => 'Неверный код. Осталось: ' . $rem, 'show_captcha' => ($failed >= $cap_at), 'remaining' => $rem]);
    }
}

// ============================================================
// SEO module — full AIOSEO replacement
// ============================================================

function vip_seo_register_panel($data) {
    static $panels = [];
    if ($data === '__get__') return $panels;
    $panels[] = $data;
}

function vip_seo_get_panels() {
    return vip_seo_register_panel('__get__');
}

function vip_seo_first_panel() {
    $panels = vip_seo_get_panels();
    return $panels ? $panels[0] : null;
}

function vip_seo_detect_plugin() {
    if (defined('WPSEO_VERSION'))             return 'yoast';
    if (defined('RANK_MATH_VERSION'))         return 'rankmath';
    if (defined('AIOSEO_VERSION') || defined('AIOSEO_FILE')) return 'aioseo';
    if (defined('SEOPRESS_VERSION'))          return 'seopress';
    if (defined('THE_SEO_FRAMEWORK_VERSION')) return 'tsf';
    return false;
}

function vip_seo_text_excerpt($text, $words = 30) {
    $text = wp_strip_all_tags((string) $text);
    return wp_trim_words($text, $words, '…');
}

function vip_seo_resolve_teaser($shortcode_teaser = '') {
    $shortcode_teaser = trim((string) $shortcode_teaser);
    if ($shortcode_teaser !== '') return $shortcode_teaser;
    $default = trim((string) get_option('vip_seo_default_teaser', ''));
    if ($default !== '') return $default;
    if (is_singular()) {
        $excerpt = trim(get_the_excerpt());
        if ($excerpt !== '') return $excerpt;
    }
    return '';
}

// Detect what kind of page we're on
function vip_seo_context() {
    if (is_404())                                      return ['type' => '404'];
    if (is_search())                                   return ['type' => 'search'];
    if (is_singular())                                 return ['type' => 'singular', 'post' => get_post()];
    if (is_front_page() || is_home())                  return ['type' => 'home'];
    if (is_category() || is_tag() || is_tax())         return ['type' => 'term', 'term' => get_queried_object()];
    if (is_post_type_archive())                        return ['type' => 'pt_archive', 'pt' => get_query_var('post_type')];
    if (is_author())                                   return ['type' => 'author', 'user' => get_queried_object()];
    if (is_date())                                     return ['type' => 'date'];
    return null;
}

// Resolve title/desc/canonical/robots/og_image for the current context
function vip_seo_resolve_context() {
    $ctx = vip_seo_context();
    if (!$ctx) return null;
    $default_og = trim((string) get_option('vip_seo_default_og_image', ''));
    $sitename = get_bloginfo('name');
    $tagline = get_bloginfo('description');
    $robots = 'index,follow';
    $kw = '';
    $og_image = $default_og;

    switch ($ctx['type']) {
        case 'singular':
            $post = $ctx['post'];
            if (!$post) return null;
            $pm = function($k) use ($post) { return trim((string) get_post_meta($post->ID, $k, true)); };
            $panel = vip_seo_first_panel();
            $title = $pm('_vip_seo_title') ?: (($panel && $panel['seo_title']) ? $panel['seo_title'] : get_the_title($post));
            $desc_raw = $pm('_vip_seo_desc') ?: (($panel && $panel['seo_desc']) ? $panel['seo_desc'] : vip_seo_resolve_teaser($panel ? $panel['teaser'] : ''));
            $kw = $pm('_vip_seo_keywords') ?: ($panel ? $panel['keywords'] : '');
            $robots = $pm('_vip_seo_robots') ?: 'index,follow';
            $canonical = $pm('_vip_seo_canonical') ?: get_permalink($post);
            $og_image = $pm('_vip_seo_og_image') ?: (get_the_post_thumbnail_url($post, 'large') ?: $default_og);
            break;

        case 'home':
            $front_id = (int) get_option('page_on_front');
            if ($front_id) {
                $title = get_the_title($front_id) ?: $sitename;
                $desc_raw = trim((string) get_post_meta($front_id, '_vip_seo_desc', true)) ?: $tagline;
                $og_image = trim((string) get_post_meta($front_id, '_vip_seo_og_image', true)) ?: (get_the_post_thumbnail_url($front_id, 'large') ?: $default_og);
            } else {
                $title = $sitename;
                $desc_raw = $tagline;
            }
            $canonical = home_url('/');
            break;

        case 'term':
            $term = $ctx['term'];
            $title = single_term_title('', false);
            $term_desc = trim((string) term_description($term));
            if ($term_desc) {
                $desc_raw = $term_desc;
            } else {
                $tpl = trim((string) get_option('vip_seo_archive_desc', ''));
                $desc_raw = $tpl ? strtr($tpl, ['%name%' => $term->name, '%sitename%' => $sitename]) : ($term->name . ' — ' . $sitename);
            }
            $canonical = get_term_link($term);
            if (is_wp_error($canonical)) $canonical = home_url(add_query_arg([], $GLOBALS['wp']->request));
            break;

        case 'pt_archive':
            $pt_obj = get_post_type_object($ctx['pt']);
            $title = $pt_obj ? $pt_obj->labels->name : ucfirst((string) $ctx['pt']);
            $desc_raw = $pt_obj && !empty($pt_obj->description) ? $pt_obj->description : ($title . ' — ' . $sitename);
            $canonical = get_post_type_archive_link($ctx['pt']) ?: home_url();
            break;

        case 'author':
            $u = $ctx['user'];
            $title = $u ? $u->display_name : 'Автор';
            $bio = $u ? trim((string) get_the_author_meta('description', $u->ID)) : '';
            $desc_raw = $bio ?: ($title . ' — публикации на ' . $sitename);
            $canonical = $u ? get_author_posts_url($u->ID) : home_url();
            break;

        case 'date':
            $title = wp_get_document_title();
            $desc_raw = 'Архив публикаций — ' . $sitename;
            $canonical = home_url(add_query_arg([], $GLOBALS['wp']->request));
            break;

        case 'search':
            $title = 'Поиск: ' . get_search_query();
            $desc_raw = '';
            $robots = 'noindex,follow';
            $canonical = home_url('/?s=' . rawurlencode(get_search_query()));
            break;

        case '404':
            $title = 'Страница не найдена';
            $desc_raw = '';
            $robots = 'noindex,follow';
            $canonical = '';
            break;
    }

    // Pagination noindex
    if (get_option('vip_seo_noindex_paged', '1') === '1') {
        $paged = max((int) get_query_var('paged'), (int) get_query_var('page'));
        if ($paged > 1 && !in_array($ctx['type'], ['singular', '404', 'search'], true)) {
            $robots = 'noindex,follow';
        }
    }

    $desc = vip_seo_text_excerpt($desc_raw, 30);
    return compact('title', 'desc', 'kw', 'robots', 'canonical', 'og_image') + ['ctx' => $ctx];
}

// Backwards-compat shim for vip_seo_filter_meta_desc_for_others / metabox-based meta access.
function vip_seo_resolve($post) {
    if (!$post) return null;
    return vip_seo_resolve_context();
}

// Image dimensions: try to find local attachment, cache result for 12h
function vip_seo_image_dims($url) {
    if (!$url) return [0, 0];
    $key = 'vip_imgd_' . md5($url);
    $cached = get_transient($key);
    if (is_array($cached)) return $cached;
    $w = 0; $h = 0;
    $att_id = function_exists('attachment_url_to_postid') ? attachment_url_to_postid($url) : 0;
    if ($att_id) {
        $meta = wp_get_attachment_metadata($att_id);
        if (!empty($meta['width']) && !empty($meta['height'])) {
            $w = (int) $meta['width']; $h = (int) $meta['height'];
        }
    }
    set_transient($key, [$w, $h], 12 * HOUR_IN_SECONDS);
    return [$w, $h];
}

// Force https on same-host URLs when site is https
function vip_seo_normalize_url($url) {
    if (!$url) return $url;
    if (is_ssl() && strpos($url, 'http://') === 0) {
        $home = wp_parse_url(home_url(), PHP_URL_HOST);
        $u_host = wp_parse_url($url, PHP_URL_HOST);
        if ($home && $u_host && $home === $u_host) {
            return 'https://' . substr($url, 7);
        }
    }
    return $url;
}

// Title formatting
function vip_seo_format_title($post_title) {
    $sep = get_option('vip_seo_title_sep', '—');
    $fmt = get_option('vip_seo_title_format', '%title% %sep% %sitename%');
    return strtr($fmt, [
        '%title%'    => $post_title,
        '%sitename%' => get_bloginfo('name'),
        '%tagline%'  => get_bloginfo('description'),
        '%sep%'      => $sep,
    ]);
}

// Should we run? Respect detection unless override is on.
function vip_seo_should_run() {
    if (get_option('vip_seo_enabled', '1') !== '1') return false;
    $override = get_option('vip_seo_override_plugin', '0') === '1';
    if (!$override && vip_seo_detect_plugin()) return false;
    return true;
}

// Whether the SEO module should output anything in the current context
function vip_seo_target_active() {
    if (get_option('vip_seo_apply_all', '1') === '1') {
        // applies to all relevant contexts (home, singular, archives, search, 404)
        return vip_seo_context() !== null;
    }
    // legacy mode: only on singular pages with [panelVIP]
    return is_singular() && vip_seo_first_panel() !== null;
}

// === <title> ===
add_filter('pre_get_document_title', 'vip_seo_filter_title', 99);
function vip_seo_filter_title($title) {
    if (!vip_seo_should_run() || !vip_seo_target_active()) return $title;
    $data = vip_seo_resolve_context();
    if (!$data) return $title;
    return vip_seo_format_title($data['title']);
}

// === robots — merge into existing array, do not replace ===
add_filter('wp_robots', 'vip_seo_filter_robots', 99);
function vip_seo_filter_robots($robots) {
    if (!vip_seo_should_run() || !vip_seo_target_active()) return $robots;
    $data = vip_seo_resolve_context();
    if (!$data) return $robots;
    $tokens = array_map('trim', explode(',', strtolower($data['robots'])));
    $valid = ['index', 'follow', 'noindex', 'nofollow', 'noarchive', 'nosnippet', 'noimageindex', 'notranslate'];
    foreach ($tokens as $t) {
        if (!in_array($t, $valid, true)) continue;
        // Mutually exclusive pairs: setting one removes its opposite
        if ($t === 'noindex')   unset($robots['index']);
        if ($t === 'index')     unset($robots['noindex']);
        if ($t === 'nofollow')  unset($robots['follow']);
        if ($t === 'follow')    unset($robots['nofollow']);
        $robots[$t] = true;
    }
    return $robots;
}

// === canonical (override core only when custom canonical is set on a post) ===
add_filter('get_canonical_url', 'vip_seo_filter_canonical', 99, 2);
function vip_seo_filter_canonical($url, $post) {
    if (!vip_seo_should_run() || !vip_seo_target_active() || !$post) return $url;
    $custom = trim((string) get_post_meta($post->ID, '_vip_seo_canonical', true));
    return $custom ?: $url;
}

// === Webmaster verification meta — emit very early ===
add_action('wp_head', 'vip_seo_emit_verification', 1);
function vip_seo_emit_verification() {
    $map = [
        'google-site-verification' => 'vip_seo_verify_google',
        'yandex-verification'      => 'vip_seo_verify_yandex',
        'msvalidate.01'            => 'vip_seo_verify_bing',
        'p:domain_verify'          => 'vip_seo_verify_pinterest',
    ];
    foreach ($map as $name => $opt) {
        $val = trim((string) get_option($opt, ''));
        if ($val !== '') {
            echo '<meta name="' . esc_attr($name) . '" content="' . esc_attr($val) . '">' . "\n";
        }
    }
}

// Build the publisher node used in multiple schema graphs
function vip_seo_publisher_node() {
    $org_name = trim((string) get_option('vip_seo_org_name', '')) ?: get_bloginfo('name');
    $org_logo = vip_seo_normalize_url(trim((string) get_option('vip_seo_org_logo', '')));
    $node = ['@type' => 'Organization', '@id' => home_url('/#organization'), 'name' => $org_name, 'url' => home_url('/')];
    if ($org_logo) {
        list($w, $h) = vip_seo_image_dims($org_logo);
        $logo = ['@type' => 'ImageObject', 'url' => $org_logo];
        if ($w && $h) { $logo['width'] = $w; $logo['height'] = $h; }
        $node['logo'] = $logo;
    }
    return $node;
}

// Build BreadcrumbList schema for the current context
function vip_seo_breadcrumbs($ctx) {
    if (get_option('vip_seo_breadcrumbs', '1') !== '1') return null;
    if (in_array($ctx['type'], ['home', '404', 'search'], true)) return null;

    $items = [['name' => 'Главная', 'url' => home_url('/')]];

    if ($ctx['type'] === 'singular') {
        $post = $ctx['post'];
        if ($post && $post->post_type === 'post') {
            $cats = get_the_category($post->ID);
            if ($cats) {
                $cat = $cats[0];
                $ancestors = array_reverse(get_ancestors($cat->term_id, 'category'));
                foreach ($ancestors as $aid) {
                    $a = get_term($aid, 'category');
                    if (!is_wp_error($a) && $a) $items[] = ['name' => $a->name, 'url' => get_term_link($a)];
                }
                $items[] = ['name' => $cat->name, 'url' => get_term_link($cat)];
            }
        } elseif ($post && $post->post_type !== 'page') {
            $pt = get_post_type_object($post->post_type);
            if ($pt && $pt->has_archive) {
                $items[] = ['name' => $pt->labels->name, 'url' => get_post_type_archive_link($post->post_type)];
            }
        }
        if ($post) $items[] = ['name' => get_the_title($post), 'url' => get_permalink($post)];
    } elseif ($ctx['type'] === 'term') {
        $term = $ctx['term'];
        $ancestors = array_reverse(get_ancestors($term->term_id, $term->taxonomy));
        foreach ($ancestors as $aid) {
            $a = get_term($aid, $term->taxonomy);
            if (!is_wp_error($a) && $a) $items[] = ['name' => $a->name, 'url' => get_term_link($a)];
        }
        $items[] = ['name' => $term->name, 'url' => get_term_link($term)];
    } elseif ($ctx['type'] === 'pt_archive') {
        $pt = get_post_type_object($ctx['pt']);
        if ($pt) $items[] = ['name' => $pt->labels->name, 'url' => get_post_type_archive_link($ctx['pt'])];
    } elseif ($ctx['type'] === 'author') {
        $u = $ctx['user'];
        if ($u) $items[] = ['name' => $u->display_name, 'url' => get_author_posts_url($u->ID)];
    } elseif ($ctx['type'] === 'date') {
        $items[] = ['name' => wp_get_document_title(), 'url' => home_url(add_query_arg([], $GLOBALS['wp']->request))];
    }

    if (count($items) < 2) return null;

    $list = [];
    foreach ($items as $i => $it) {
        $url = is_string($it['url']) ? $it['url'] : '';
        $list[] = [
            '@type' => 'ListItem',
            'position' => $i + 1,
            'name' => $it['name'],
            'item' => vip_seo_normalize_url($url),
        ];
    }
    return ['@context' => 'https://schema.org', '@type' => 'BreadcrumbList', 'itemListElement' => $list];
}

// === <head> meta tags + Schema.org ===
add_action('wp_head', 'vip_seo_emit', 5);
function vip_seo_emit() {
    if (!vip_seo_should_run() || !vip_seo_target_active()) return;
    $d = vip_seo_resolve_context();
    if (!$d) return;
    $ctx = $d['ctx'];
    $is_panel = vip_seo_first_panel() !== null;
    $sitename = get_bloginfo('name');

    $og_image = vip_seo_normalize_url($d['og_image']);
    list($img_w, $img_h) = $og_image ? vip_seo_image_dims($og_image) : [0, 0];
    $og_type = ($ctx['type'] === 'singular' && $ctx['post'] && $ctx['post']->post_type === 'post') ? 'article' : 'website';

    echo "\n<!-- VIP Content Locker SEO -->\n";

    if ($d['desc']) echo '<meta name="description" content="' . esc_attr($d['desc']) . '">' . "\n";
    if ($d['kw'])   echo '<meta name="keywords" content="' . esc_attr($d['kw']) . '">' . "\n";

    // Canonical: WP core emits it for singular automatically (we hooked get_canonical_url).
    // For non-singular contexts, emit ourselves.
    if ($d['canonical'] && $ctx['type'] !== 'singular' && $ctx['type'] !== '404') {
        echo '<link rel="canonical" href="' . esc_url(vip_seo_normalize_url($d['canonical'])) . '">' . "\n";
    }

    // Open Graph
    echo '<meta property="og:type" content="' . esc_attr($og_type) . '">' . "\n";
    echo '<meta property="og:title" content="' . esc_attr($d['title']) . '">' . "\n";
    if ($d['desc']) echo '<meta property="og:description" content="' . esc_attr($d['desc']) . '">' . "\n";
    if ($d['canonical']) echo '<meta property="og:url" content="' . esc_url(vip_seo_normalize_url($d['canonical'])) . '">' . "\n";
    echo '<meta property="og:site_name" content="' . esc_attr($sitename) . '">' . "\n";
    echo '<meta property="og:locale" content="' . esc_attr(get_locale()) . '">' . "\n";
    if ($og_image) {
        echo '<meta property="og:image" content="' . esc_url($og_image) . '">' . "\n";
        echo '<meta property="og:image:secure_url" content="' . esc_url($og_image) . '">' . "\n";
        if ($img_w) echo '<meta property="og:image:width" content="' . (int) $img_w . '">' . "\n";
        if ($img_h) echo '<meta property="og:image:height" content="' . (int) $img_h . '">' . "\n";
        echo '<meta property="og:image:alt" content="' . esc_attr($d['title']) . '">' . "\n";
    }

    // article:* tags only for blog posts
    if ($og_type === 'article' && $ctx['type'] === 'singular') {
        $post = $ctx['post'];
        echo '<meta property="article:published_time" content="' . esc_attr(get_the_date('c', $post)) . '">' . "\n";
        echo '<meta property="article:modified_time" content="' . esc_attr(get_the_modified_date('c', $post)) . '">' . "\n";
        $author_name = get_the_author_meta('display_name', $post->post_author);
        if ($author_name) echo '<meta property="article:author" content="' . esc_attr($author_name) . '">' . "\n";
        $cats = get_the_category($post->ID);
        if ($cats) echo '<meta property="article:section" content="' . esc_attr($cats[0]->name) . '">' . "\n";
        $tags = get_the_tags($post->ID);
        if ($tags) {
            foreach ($tags as $t) echo '<meta property="article:tag" content="' . esc_attr($t->name) . '">' . "\n";
        }
    }

    // Twitter Cards
    echo '<meta name="twitter:card" content="' . ($og_image ? 'summary_large_image' : 'summary') . '">' . "\n";
    echo '<meta name="twitter:title" content="' . esc_attr($d['title']) . '">' . "\n";
    if ($d['desc']) echo '<meta name="twitter:description" content="' . esc_attr($d['desc']) . '">' . "\n";
    if ($og_image)  echo '<meta name="twitter:image" content="' . esc_url($og_image) . '">' . "\n";
    $tw_site = trim((string) get_option('vip_seo_twitter_site', ''));
    if ($tw_site) echo '<meta name="twitter:site" content="' . esc_attr($tw_site) . '">' . "\n";
    if ($ctx['type'] === 'singular' && $ctx['post']) {
        $tw_creator = trim((string) get_the_author_meta('twitter', $ctx['post']->post_author));
        if ($tw_creator) {
            if (strpos($tw_creator, '@') !== 0) $tw_creator = '@' . $tw_creator;
            echo '<meta name="twitter:creator" content="' . esc_attr($tw_creator) . '">' . "\n";
        }
    }

    // Schema.org graph
    $graph = [];

    // Organization (always)
    $graph[] = vip_seo_publisher_node();

    // WebSite (always) — adds SearchAction (sitelinks search box)
    $graph[] = [
        '@type' => 'WebSite',
        '@id'   => home_url('/#website'),
        'url'   => home_url('/'),
        'name'  => $sitename,
        'description' => get_bloginfo('description'),
        'publisher' => ['@id' => home_url('/#organization')],
        'potentialAction' => [[
            '@type' => 'SearchAction',
            'target' => ['@type' => 'EntryPoint', 'urlTemplate' => home_url('/?s={search_term_string}')],
            'query-input' => 'required name=search_term_string',
        ]],
        'inLanguage' => get_locale(),
    ];

    // Article (only for blog posts)
    if ($og_type === 'article' && $ctx['type'] === 'singular') {
        $post = $ctx['post'];
        $word_count = str_word_count(wp_strip_all_tags((string) $post->post_content));
        $article = [
            '@type' => 'Article',
            '@id'   => $d['canonical'] . '#article',
            'mainEntityOfPage' => ['@type' => 'WebPage', '@id' => $d['canonical']],
            'headline' => $d['title'],
            'datePublished' => get_the_date('c', $post),
            'dateModified' => get_the_modified_date('c', $post),
            'author' => ['@type' => 'Person', 'name' => get_the_author_meta('display_name', $post->post_author)],
            'publisher' => ['@id' => home_url('/#organization')],
            'inLanguage' => get_locale(),
        ];
        if ($d['desc'])     $article['description'] = $d['desc'];
        if ($og_image)      $article['image'] = $og_image;
        if ($d['kw'])       $article['keywords'] = $d['kw'];
        if ($word_count)    $article['wordCount'] = $word_count;
        if ($is_panel) {
            $article['isAccessibleForFree'] = false;
            $article['hasPart'] = [
                '@type' => 'WebPageElement',
                'isAccessibleForFree' => false,
                'cssSelector' => '.vip-lock-overlay',
            ];
        }
        $graph[] = $article;
    }

    // BreadcrumbList
    $bc = vip_seo_breadcrumbs($ctx);
    if ($bc) {
        unset($bc['@context']);
        $graph[] = $bc;
    }

    echo '<script type="application/ld+json">' . wp_json_encode([
        '@context' => 'https://schema.org',
        '@graph' => $graph,
    ], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) . '</script>' . "\n";

    echo "<!-- /VIP Content Locker SEO -->\n";
}

// === SEO score — server-side calculation (used by metabox initial state and admin column) ===
function vip_seo_score($post_id) {
    $post = get_post($post_id);
    if (!$post) return ['score' => 0, 'checks' => []];
    $title = trim((string) get_post_meta($post_id, '_vip_seo_title', true)) ?: get_the_title($post);
    $desc  = trim((string) get_post_meta($post_id, '_vip_seo_desc', true));
    $kw    = trim((string) get_post_meta($post_id, '_vip_seo_keywords', true));
    $focus = mb_strtolower(trim((string) get_post_meta($post_id, '_vip_seo_focus_kw', true)));
    $og    = trim((string) get_post_meta($post_id, '_vip_seo_og_image', true));
    $content = mb_strtolower(wp_strip_all_tags((string) $post->post_content));
    $title_l = mb_strtolower($title);
    $desc_l = mb_strtolower($desc);
    $has_image = $og || has_post_thumbnail($post_id) || trim((string) get_option('vip_seo_default_og_image', ''));

    $checks = [
        'title'         => $title !== '',
        'title_len'     => mb_strlen($title) >= 30 && mb_strlen($title) <= 60,
        'desc'          => $desc !== '',
        'desc_len'      => mb_strlen($desc) >= 120 && mb_strlen($desc) <= 160,
        'kw'            => $kw !== '',
        'focus'         => $focus !== '',
        'focus_title'   => $focus !== '' && mb_strpos($title_l, $focus) !== false,
        'focus_desc'    => $focus !== '' && mb_strpos($desc_l, $focus) !== false,
        'focus_content' => $focus !== '' && mb_strpos($content, $focus) !== false,
        'image'         => (bool) $has_image,
    ];
    $weights = ['title'=>15,'title_len'=>10,'desc'=>15,'desc_len'=>15,'kw'=>10,'focus'=>5,'focus_title'=>10,'focus_desc'=>10,'focus_content'=>5,'image'=>5];
    $score = 0;
    foreach ($weights as $k => $w) if (!empty($checks[$k])) $score += $w;
    return ['score' => $score, 'checks' => $checks];
}

function vip_seo_score_color($score) {
    if ($score < 40) return '#d63638';
    if ($score < 70) return '#dba617';
    if ($score < 90) return '#8ec457';
    return '#00a32a';
}

// === SEO column in posts list ===
add_action('admin_init', 'vip_seo_register_columns');
function vip_seo_register_columns() {
    foreach (get_post_types(['public' => true]) as $pt) {
        if ($pt === 'attachment') continue;
        add_filter("manage_{$pt}_posts_columns", 'vip_seo_add_column');
        add_action("manage_{$pt}_posts_custom_column", 'vip_seo_render_column', 10, 2);
    }
}

function vip_seo_add_column($cols) {
    $new = [];
    foreach ($cols as $k => $v) {
        $new[$k] = $v;
        if ($k === 'title') $new['vip_seo'] = 'SEO';
    }
    if (!isset($new['vip_seo'])) $new['vip_seo'] = 'SEO';
    return $new;
}

function vip_seo_render_column($column, $post_id) {
    if ($column !== 'vip_seo') return;
    $data = vip_seo_score($post_id);
    $score = (int) $data['score'];
    $color = vip_seo_score_color($score);
    echo '<div title="SEO ' . $score . '%" style="display:inline-flex;align-items:center;gap:8px;min-width:90px">';
    echo '<div style="flex:1;height:6px;background:#e0e0e0;border-radius:999px;overflow:hidden"><div style="width:' . $score . '%;height:100%;background:' . esc_attr($color) . ';border-radius:999px"></div></div>';
    echo '<span style="font-weight:600;color:' . esc_attr($color) . ';font-size:12px;min-width:34px;text-align:right">' . $score . '%</span>';
    echo '</div>';
}

// Add Twitter field to user profile so authors can set their @handle
add_filter('user_contactmethods', 'vip_seo_user_contactmethods');
function vip_seo_user_contactmethods($methods) {
    if (!isset($methods['twitter'])) $methods['twitter'] = 'Twitter / X (без @)';
    return $methods;
}

// Light integration with Yoast / Rank Math (active only when override is OFF)
add_filter('wpseo_metadesc', 'vip_seo_filter_meta_desc_for_others', 9);
add_filter('rank_math/frontend/description', 'vip_seo_filter_meta_desc_for_others', 9);
function vip_seo_filter_meta_desc_for_others($desc) {
    if (!empty($desc) || !is_singular()) return $desc;
    $post = get_post();
    if (!$post) return $desc;
    $custom = trim((string) get_post_meta($post->ID, '_vip_seo_desc', true));
    if ($custom) return vip_seo_text_excerpt($custom, 30);
    $panel = vip_seo_first_panel();
    if ($panel) {
        $candidate = $panel['seo_desc'] ?: vip_seo_resolve_teaser($panel['teaser']);
        if ($candidate) return vip_seo_text_excerpt($candidate, 30);
    }
    return $desc;
}

// === Per-post meta box ===
add_action('add_meta_boxes', 'vip_seo_metabox_register');
function vip_seo_metabox_register() {
    foreach (get_post_types(['public' => true]) as $pt) {
        if ($pt === 'attachment') continue;
        add_meta_box('vip_seo_box', 'VIP SEO', 'vip_seo_metabox_render', $pt, 'normal', 'high');
    }
}

function vip_seo_metabox_render($post) {
    wp_nonce_field('vip_seo_save_' . $post->ID, 'vip_seo_nonce');
    $f = function($k) use ($post) { return esc_attr(get_post_meta($post->ID, $k, true)); };
    $robots = get_post_meta($post->ID, '_vip_seo_robots', true) ?: 'index,follow';
    $desc_val = get_post_meta($post->ID, '_vip_seo_desc', true);
    $title_val = get_post_meta($post->ID, '_vip_seo_title', true);
    $focus_val = get_post_meta($post->ID, '_vip_seo_focus_kw', true);
    $sep = get_option('vip_seo_title_sep', '—');
    $sitename = get_bloginfo('name');
    $score_data = vip_seo_score($post->ID);
    $perma = get_permalink($post) ?: home_url('/?p=' . $post->ID);
    $perma_pretty = preg_replace('#^https?://#', '', untrailingslashit($perma));
    ?>
    <style>
        .vip-seo-wrap { font-size: 13px; }
        .vip-seo-grid { display: grid; gap: 14px; }
        .vip-seo-grid label { font-weight: 600; display: block; margin-bottom: 4px; }
        .vip-seo-grid .help { color: #666; font-size: 12px; margin-top: 2px; }
        .vip-seo-grid input[type=text], .vip-seo-grid input[type=url], .vip-seo-grid textarea, .vip-seo-grid select { width: 100%; }
        .vip-seo-score { display: flex; align-items: center; gap: 12px; padding: 12px 14px; background: #f6f7f7; border: 1px solid #dcdcde; border-radius: 6px; margin-bottom: 14px; }
        .vip-seo-score-bar { flex: 1; height: 10px; background: #e0e0e0; border-radius: 999px; overflow: hidden; }
        .vip-seo-score-fill { height: 100%; width: 0%; transition: width .35s ease, background-color .35s ease; background: #d63638; border-radius: 999px; }
        .vip-seo-score-pct { font-size: 18px; font-weight: 700; min-width: 56px; text-align: right; color: #1d2327; }
        .vip-seo-score-label { font-weight: 600; }
        .vip-seo-checks { margin: 0; padding: 0; list-style: none; display: grid; grid-template-columns: repeat(2, 1fr); gap: 4px 16px; font-size: 12px; }
        .vip-seo-checks li::before { content: "○ "; color: #999; }
        .vip-seo-checks li.ok::before { content: "✓ "; color: #00a32a; font-weight: bold; }
        .vip-seo-checks li.warn::before { content: "⚠ "; color: #dba617; }
        .vip-seo-checks li.fail::before { content: "✗ "; color: #d63638; }
        .vip-seo-snippet { background: #fff; border: 1px solid #dcdcde; border-radius: 6px; padding: 14px; margin-bottom: 14px; font-family: arial, sans-serif; }
        .vip-seo-snippet-host { font-size: 12px; color: #202124; }
        .vip-seo-snippet-title { color: #1a0dab; font-size: 18px; line-height: 1.3; margin: 4px 0 4px; word-wrap: break-word; }
        .vip-seo-snippet-desc { color: #4d5156; font-size: 13px; line-height: 1.4; word-wrap: break-word; }
        .vip-seo-counter { font-weight: 400; color: #666; font-size: 11px; }
        .vip-seo-counter.bad { color: #d63638; }
        .vip-seo-counter.ok { color: #00a32a; }
    </style>
    <div class="vip-seo-wrap">
        <div class="vip-seo-score" data-score="<?php echo (int) $score_data['score']; ?>">
            <span class="vip-seo-score-label">SEO качество</span>
            <div class="vip-seo-score-bar"><div class="vip-seo-score-fill" id="vip-seo-fill"></div></div>
            <span class="vip-seo-score-pct" id="vip-seo-pct">0%</span>
        </div>
        <ul class="vip-seo-checks" id="vip-seo-checks">
            <li data-check="title">SEO Title заполнен</li>
            <li data-check="title_len">Длина title 30–60</li>
            <li data-check="desc">Meta Description заполнено</li>
            <li data-check="desc_len">Длина description 120–160</li>
            <li data-check="kw">Ключевые слова заданы</li>
            <li data-check="focus">Указан фокус-ключ</li>
            <li data-check="focus_title">Фокус-ключ в заголовке</li>
            <li data-check="focus_desc">Фокус-ключ в описании</li>
            <li data-check="focus_content">Фокус-ключ в тексте</li>
            <li data-check="image">OG/thumbnail-картинка</li>
        </ul>

        <div class="vip-seo-snippet" aria-hidden="true">
            <div class="vip-seo-snippet-host"><?php echo esc_html($perma_pretty); ?></div>
            <div class="vip-seo-snippet-title" id="vip-seo-snippet-title">—</div>
            <div class="vip-seo-snippet-desc" id="vip-seo-snippet-desc">—</div>
        </div>

        <div class="vip-seo-grid">
            <div>
                <label>Фокус-ключ (главное ключевое слово)</label>
                <input type="text" id="vip-seo-focus" name="_vip_seo_focus_kw" value="<?php echo $f('_vip_seo_focus_kw'); ?>" placeholder="например: гайд по колоде охотника">
                <div class="help">Используется для проверки наличия в title/description/тексте.</div>
            </div>
            <div>
                <label>SEO Title <span class="vip-seo-counter" id="vip-seo-title-c">0/60</span></label>
                <input type="text" id="vip-seo-title" name="_vip_seo_title" value="<?php echo esc_attr($title_val); ?>" placeholder="<?php echo esc_attr(get_the_title($post)); ?>">
                <div class="help">Оптимально 30–60 символов. К значению применится формат из настроек.</div>
            </div>
            <div>
                <label>Meta Description <span class="vip-seo-counter" id="vip-seo-desc-c">0/160</span></label>
                <textarea id="vip-seo-desc" name="_vip_seo_desc" rows="3" maxlength="300"><?php echo esc_textarea($desc_val); ?></textarea>
                <div class="help">Оптимально 120–160 символов.</div>
            </div>
            <div>
                <label>Keywords (через запятую)</label>
                <input type="text" name="_vip_seo_keywords" value="<?php echo $f('_vip_seo_keywords'); ?>" placeholder="hearthstone, колода, гайд">
            </div>
            <div>
                <label>Robots</label>
                <select name="_vip_seo_robots">
                    <?php foreach (['index,follow','noindex,follow','index,nofollow','noindex,nofollow'] as $opt): ?>
                        <option value="<?php echo esc_attr($opt); ?>" <?php selected($robots, $opt); ?>><?php echo esc_html($opt); ?></option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div>
                <label>Canonical URL (необязательно)</label>
                <input type="url" name="_vip_seo_canonical" value="<?php echo $f('_vip_seo_canonical'); ?>" placeholder="<?php echo esc_attr($perma); ?>">
                <div class="help">Указывайте только если статья дубль или должна указывать на другой URL.</div>
            </div>
            <div>
                <label>OG-картинка (URL, необязательно)</label>
                <input type="url" id="vip-seo-og" name="_vip_seo_og_image" value="<?php echo $f('_vip_seo_og_image'); ?>" placeholder="https://example.com/share.jpg">
                <div class="help">Если пусто — используется thumbnail записи или картинка по умолчанию из настроек.</div>
            </div>
        </div>
    </div>
    <script>
    (function(){
        var $title = document.getElementById('vip-seo-title');
        var $desc = document.getElementById('vip-seo-desc');
        var $focus = document.getElementById('vip-seo-focus');
        var $og = document.getElementById('vip-seo-og');
        var $sTitle = document.getElementById('vip-seo-snippet-title');
        var $sDesc = document.getElementById('vip-seo-snippet-desc');
        var $titleC = document.getElementById('vip-seo-title-c');
        var $descC = document.getElementById('vip-seo-desc-c');
        var $fill = document.getElementById('vip-seo-fill');
        var $pct = document.getElementById('vip-seo-pct');
        var $checks = document.getElementById('vip-seo-checks');
        var sep = <?php echo wp_json_encode($sep); ?>;
        var sitename = <?php echo wp_json_encode($sitename); ?>;
        var fallbackTitle = <?php echo wp_json_encode(get_the_title($post)); ?>;
        var hasThumb = <?php echo has_post_thumbnail($post->ID) ? 'true' : 'false'; ?>;
        var defaultOg = <?php echo wp_json_encode(get_option('vip_seo_default_og_image', '')); ?>;

        function getEditorContent() {
            try {
                if (window.tinymce && window.tinymce.activeEditor && !window.tinymce.activeEditor.isHidden()) {
                    return window.tinymce.activeEditor.getContent({format: 'text'}) || '';
                }
            } catch (e) {}
            try {
                if (window.wp && window.wp.data && window.wp.data.select('core/editor')) {
                    var c = window.wp.data.select('core/editor').getEditedPostContent();
                    var d = document.createElement('div'); d.innerHTML = c || '';
                    return d.textContent || '';
                }
            } catch (e) {}
            var ta = document.getElementById('content');
            return ta ? ta.value : '';
        }

        function score() {
            var t = ($title.value || fallbackTitle).trim();
            var d = ($desc.value || '').trim();
            var k = $focus.value.trim().toLowerCase();
            var content = getEditorContent().toLowerCase();
            var kwField = (document.querySelector('[name=_vip_seo_keywords]') || {value:''}).value.trim();
            var ogVal = $og.value.trim();
            var hasImage = !!(ogVal || hasThumb || defaultOg);

            var checks = {
                title: !!t,
                title_len: t.length >= 30 && t.length <= 60,
                desc: !!d,
                desc_len: d.length >= 120 && d.length <= 160,
                kw: !!kwField,
                focus: !!k,
                focus_title: !!k && t.toLowerCase().indexOf(k) !== -1,
                focus_desc: !!k && d.toLowerCase().indexOf(k) !== -1,
                focus_content: !!k && content.indexOf(k) !== -1,
                image: hasImage,
            };
            var weights = {title:15, title_len:10, desc:15, desc_len:15, kw:10, focus:5, focus_title:10, focus_desc:10, focus_content:5, image:5};
            var pct = 0;
            for (var key in weights) if (checks[key]) pct += weights[key];

            $fill.style.width = pct + '%';
            $fill.style.background = pct < 40 ? '#d63638' : pct < 70 ? '#dba617' : pct < 90 ? '#8ec457' : '#00a32a';
            $pct.textContent = pct + '%';

            $checks.querySelectorAll('li').forEach(function(li){
                var name = li.getAttribute('data-check');
                li.classList.remove('ok','warn','fail');
                if (checks[name]) li.classList.add('ok');
                else if (name === 'focus_title' || name === 'focus_desc' || name === 'focus_content') {
                    li.classList.add(k ? 'fail' : 'warn');
                } else li.classList.add('fail');
            });

            // counters
            var tl = t.length;
            $titleC.textContent = tl + '/60';
            $titleC.className = 'vip-seo-counter ' + (tl >= 30 && tl <= 60 ? 'ok' : (tl > 0 ? 'bad' : ''));
            var dl = d.length;
            $descC.textContent = dl + '/160';
            $descC.className = 'vip-seo-counter ' + (dl >= 120 && dl <= 160 ? 'ok' : (dl > 0 ? 'bad' : ''));

            // snippet preview
            var fullTitle = t || fallbackTitle;
            $sTitle.textContent = fullTitle + ' ' + sep + ' ' + sitename;
            $sDesc.textContent = d || '—';
        }

        ['input','change','keyup'].forEach(function(ev){
            [$title, $desc, $focus, $og].forEach(function(el){ if (el) el.addEventListener(ev, score); });
            var kw = document.querySelector('[name=_vip_seo_keywords]');
            if (kw) kw.addEventListener(ev, score);
        });
        score();
    })();
    </script>
    <?php
}

add_action('save_post', 'vip_seo_metabox_save', 10, 2);
function vip_seo_metabox_save($post_id, $post) {
    if (!isset($_POST['vip_seo_nonce']) || !wp_verify_nonce($_POST['vip_seo_nonce'], 'vip_seo_save_' . $post_id)) return;
    if (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE) return;
    if (wp_is_post_revision($post_id)) return;
    if (!current_user_can('edit_post', $post_id)) return;

    $fields = [
        '_vip_seo_title'     => 'sanitize_text_field',
        '_vip_seo_desc'      => 'sanitize_textarea_field',
        '_vip_seo_keywords'  => 'sanitize_text_field',
        '_vip_seo_focus_kw'  => 'sanitize_text_field',
        '_vip_seo_robots'    => 'sanitize_text_field',
        '_vip_seo_canonical' => 'esc_url_raw',
        '_vip_seo_og_image'  => 'esc_url_raw',
    ];
    foreach ($fields as $key => $san) {
        $val = isset($_POST[$key]) ? call_user_func($san, wp_unslash($_POST[$key])) : '';
        if ($val === '') {
            delete_post_meta($post_id, $key);
        } else {
            update_post_meta($post_id, $key, $val);
        }
    }
}
?>