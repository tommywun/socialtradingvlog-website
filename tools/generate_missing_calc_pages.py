#!/usr/bin/env python3
"""Generate missing calculator pages for ms, vi, el, cs languages.
Uses existing Thai/Indonesian/Danish templates and replaces language-specific content."""

import os
import re

BASE = os.path.expanduser('~/socialtradingvlog-website')

# Language configs
LANGS = {
    'ms': {
        'code': 'ms', 'name': 'Melayu', 'dir': 'ms/kalkulator',
        'calc_slugs': {'fee': 'kalkulator-yuran', 'roi': 'kalkulator-roi', 'compare': 'bandingkan-platform', 'position': 'saiz-posisi'},
        'nav_labels': {'fee': 'Kalkulator Yuran', 'roi': 'Kalkulator ROI', 'compare': 'Bandingkan Platform'},
        'back_text': '&larr; Kembali ke laman',
        'fee': {
            'title': 'Kalkulator Yuran eToro 2026 — Kira Kos Dagangan Anda | SocialTradingVlog',
            'meta_desc': 'Kalkulator yuran eToro percuma. Ketahui dengan tepat berapa yang anda akan bayar untuk spread, yuran semalaman, pengeluaran dan penukaran mata wang. Dikemas kini untuk 2026.',
            'h1': 'Kalkulator<span class="accent">Yuran eToro</span>',
            'hero_p': 'Ketahui dengan tepat berapa yang anda akan bayar sebelum berdagang. Masukkan butiran dagangan anda dan dapatkan pecahan kos lengkap dalam beberapa saat.',
            'badge': 'Dikemas kini Februari 2026',
            'verified_label': 'Data disahkan terakhir:',
            'verified_note': ' — Kami menyemak yuran eToro setiap minggu. Sentiasa sahkan di',
            'verified_link_text': 'halaman yuran rasmi',
            'asset_label': 'Apa yang anda akan dagangkan?',
            'assets': {'stocks': 'Saham', 'crypto': 'Kripto', 'forex': 'Forex', 'commodities': 'Komoditi', 'indices': 'Indeks', 'etfs': 'ETF'},
            'amount_label': 'Jumlah dagangan',
            'period_label': 'Berapa lama anda akan memegang posisi?',
            'periods': {'intraday': 'Harian', 'week': '1 minggu', 'month': '1 bulan', 'year': '1 tahun'},
            'currency_label': 'Mata wang akaun anda',
            'results_label': 'Anggaran jumlah kos',
            'pct_suffix': '% daripada dagangan anda',
            'spread_label': 'Spread', 'spread_note': 'Yuran dagangan',
            'overnight_label': 'Yuran semalaman', 'overnight_intraday': 'Harian',
            'conversion_label': 'Penukaran', 'conversion_note': 'Yuran mata wang',
            'withdrawal_label': 'Pengeluaran', 'withdrawal_note': 'Jika anda mengeluarkan dana',
            'legend': {'spread': 'Spread', 'overnight': 'Semalaman', 'conversion': 'Penukaran', 'withdrawal': 'Pengeluaran'},
            'disclaimer_title': 'Notis ketepatan data',
            'disclaimer_text': 'Kalkulator ini memberikan <strong style="display:inline;font-size:inherit;">anggaran sahaja</strong> dan adalah untuk tujuan maklumat dan pendidikan sahaja. Ia tidak boleh digunakan sebagai asas untuk membuat keputusan kewangan.',
            'explainer_title': 'Bagaimana yuran eToro berfungsi',
            'spread_card_title': 'Spread', 'spread_card_text': 'Spread ialah perbezaan antara harga beli dan harga jual. Ia merupakan sumber pendapatan utama eToro. Saham dan ETF tanpa komisen — anda hanya membayar spread. Spread kripto bermula dari 1%.',
            'overnight_card_title': 'Yuran semalaman', 'overnight_card_text': 'Posisi CFD yang dipegang selepas 22:00 (waktu UK) dikenakan yuran semalaman harian. Kos ini terkumpul dari semasa ke semasa — posisi yang dipegang selama setahun jauh lebih mahal daripada dagangan harian. Posisi kripto dan saham sebenar dikecualikan.',
            'other_card_title': 'Yuran lain', 'other_card_text': 'Penukaran mata wang dikenakan jika mata wang akaun anda berbeza daripada aset. Pengeluaran berharga $5 untuk akaun USD (percuma untuk GBP/EUR). Terdapat yuran ketidakaktifan $10/bulan selepas 12 bulan tidak log masuk.',
            'spread_table_title': 'Jadual spread eToro lengkap',
            'table_headers': {'asset': 'Kelas aset', 'spread': 'Spread biasa', 'commission': 'Komisen', 'overnight': 'Yuran semalaman'},
            'table_rows': {'stocks_us': 'Saham (AS)', 'stocks_eu': 'Saham (EU/UK)', 'other_crypto': 'Kripto lain', 'gold': 'Emas', 'oil': 'Minyak', 'none_crypto': 'Tiada (kripto sebenar)', 'cfd_only': '(CFD sahaja)'},
            'faq_title': 'Soalan Lazim',
            'faqs': [
                ('Apakah yuran dagangan eToro?', 'eToro mengenakan yuran terutamanya melalui spread (perbezaan antara harga beli dan jual). Dagangan saham dan ETF tanpa komisen. Kripto mempunyai spread 1%. Forex bermula dari 1 pip. Kos tambahan termasuk yuran semalaman untuk posisi CFD yang dipegang selepas 22:00 waktu UK.'),
                ('Adakah eToro mengenakan yuran pengeluaran?', 'Pemegang akaun USD membayar yuran pengeluaran $5 (minimum pengeluaran $30). Pemegang akaun GBP dan EUR boleh mengeluarkan secara percuma.'),
                ('Adakah yuran tersembunyi dalam eToro?', 'Kos "tersembunyi" utama ialah yuran semalaman pada posisi CFD dan yuran penukaran mata wang jika mata wang akaun anda berbeza daripada aset. Terdapat juga yuran ketidakaktifan $10/bulan selepas 12 bulan tidak log masuk. Kalkulator ini menunjukkan semua kos ini dengan telus.'),
                ('Adakah copy trading di eToro percuma?', 'Ya, tiada yuran tambahan untuk menggunakan ciri CopyTrader eToro. Anda hanya membayar yuran dagangan standard untuk posisi yang dibuka oleh trader yang anda salin bagi pihak anda. Minimum untuk menyalin trader ialah $200.'),
                ('Berapa kos untuk berdagang kripto di eToro?', 'eToro mengenakan spread 1% untuk pembelian kripto. Tiada yuran semalaman untuk memegang kripto sebenar (bukan CFD). Memindahkan kripto ke dompet luaran berharga 2%. Spread dikenakan semasa membeli dan menjual.'),
            ],
            'cta_title': 'Bersedia untuk mula melabur?',
            'cta_text': 'Sertai eToro dan akses saham, kripto, forex dan copy trading. Mulakan dengan hanya $50.',
            'cta_btn': 'Buka akaun eToro &rarr;',
            'risk_warning': '<strong>51% akaun pelabur runcit kehilangan wang apabila berdagang CFD dengan pembekal ini.</strong> Anda harus mempertimbangkan sama ada anda mampu menanggung risiko tinggi kehilangan wang anda. Ini bukan nasihat kewangan. Modal berisiko. Pautan afiliasi: Tom mungkin menerima komisen tanpa kos tambahan kepada anda.',
            'footer_tools': 'Semua alat',
            'footer_disclaimer': 'Kalkulator ini adalah untuk tujuan maklumat sahaja dan bukan nasihat kewangan. Anggaran yuran mungkin tidak tepat atau lapuk — sentiasa sahkan di laman web rasmi eToro. SocialTradingVlog tidak bertanggungjawab atas kerugian yang timbul daripada penggunaan alat ini. eToro ialah platform pelaburan pelbagai aset. Nilai pelaburan anda boleh naik atau turun. Modal anda berisiko. 51% akaun pelabur runcit kehilangan wang apabila berdagang CFD dengan pembekal ini.',
            'unknown': 'Tidak diketahui', 'unavailable': 'Tidak tersedia',
            'day_singular': ' hari', 'free_for': 'Percuma untuk ',
            'callout_low': 'Ini hanya {pct}% daripada dagangan anda. Yuran {asset} di eToro sangat kompetitif — bank biasa mengenakan $10 hingga $25 setiap dagangan saham.',
            'callout_mid': 'Ini {pct}% daripada dagangan anda. {detail}',
            'callout_mid_overnight': 'Kebanyakan kos ini datang daripada yuran semalaman — pertimbangkan tempoh yang lebih pendek untuk mengurangkan kos.',
            'callout_mid_inline': 'Ini selaras dengan purata industri untuk dagangan {asset}.',
            'callout_high_crypto': 'Spread kripto lebih tinggi daripada saham/forex — ini biasa di semua platform.',
            'callout_high_other': 'Yuran semalaman terkumpul dari semasa ke semasa. Pertimbangkan sama ada tempoh yang lebih pendek boleh mengurangkan kos anda.',
        },
    },
    'vi': {
        'code': 'vi', 'name': 'Tiếng Việt', 'dir': 'vi/may-tinh',
        'calc_slugs': {'fee': 'tinh-phi', 'roi': 'tinh-roi', 'compare': 'so-sanh-nen-tang', 'position': 'kich-thuoc-vi-the'},
        'nav_labels': {'fee': 'Tính phí', 'roi': 'Tính lợi nhuận', 'compare': 'So sánh nền tảng'},
        'back_text': '&larr; Quay lại trang web',
        'fee': {
            'title': 'Máy tính phí eToro 2026 — Tính chi phí giao dịch của bạn | SocialTradingVlog',
            'meta_desc': 'Máy tính phí eToro miễn phí. Tìm hiểu chính xác bạn sẽ phải trả bao nhiêu cho spread, phí qua đêm, rút tiền và chuyển đổi tiền tệ. Cập nhật cho 2026.',
            'h1': 'Máy tính<span class="accent">phí eToro</span>',
            'hero_p': 'Tìm hiểu chính xác bạn sẽ phải trả bao nhiêu trước khi giao dịch. Nhập chi tiết giao dịch của bạn và nhận bảng phân tích chi phí đầy đủ trong vài giây.',
            'badge': 'Cập nhật tháng 2 năm 2026',
            'verified_label': 'Dữ liệu được xác minh lần cuối:',
            'verified_note': ' — Chúng tôi kiểm tra phí eToro hàng tuần. Luôn xác minh tại',
            'verified_link_text': 'trang phí chính thức',
            'asset_label': 'Bạn sẽ giao dịch gì?',
            'assets': {'stocks': 'Cổ phiếu', 'crypto': 'Tiền điện tử', 'forex': 'Forex', 'commodities': 'Hàng hóa', 'indices': 'Chỉ số', 'etfs': 'ETF'},
            'amount_label': 'Số tiền giao dịch',
            'period_label': 'Bạn sẽ giữ vị thế trong bao lâu?',
            'periods': {'intraday': 'Trong ngày', 'week': '1 tuần', 'month': '1 tháng', 'year': '1 năm'},
            'currency_label': 'Loại tiền tệ tài khoản của bạn',
            'results_label': 'Tổng chi phí ước tính',
            'pct_suffix': '% giao dịch của bạn',
            'spread_label': 'Spread', 'spread_note': 'Phí giao dịch',
            'overnight_label': 'Phí qua đêm', 'overnight_intraday': 'Trong ngày',
            'conversion_label': 'Chuyển đổi', 'conversion_note': 'Phí tiền tệ',
            'withdrawal_label': 'Rút tiền', 'withdrawal_note': 'Nếu bạn rút tiền',
            'legend': {'spread': 'Spread', 'overnight': 'Qua đêm', 'conversion': 'Chuyển đổi', 'withdrawal': 'Rút tiền'},
            'disclaimer_title': 'Lưu ý về độ chính xác dữ liệu',
            'explainer_title': 'Phí eToro hoạt động như thế nào',
            'spread_card_title': 'Spread', 'spread_card_text': 'Spread là chênh lệch giữa giá mua và giá bán. Đây là nguồn thu nhập chính của eToro. Cổ phiếu và ETF không có hoa hồng — bạn chỉ trả spread. Spread tiền điện tử bắt đầu từ 1%.',
            'overnight_card_title': 'Phí qua đêm', 'overnight_card_text': 'Các vị thế CFD được giữ sau 22:00 (giờ UK) sẽ phát sinh phí qua đêm hàng ngày. Chi phí này tích lũy theo thời gian — vị thế giữ trong một năm tốn nhiều hơn đáng kể so với giao dịch trong ngày. Vị thế tiền điện tử và cổ phiếu thực được miễn.',
            'other_card_title': 'Phí khác', 'other_card_text': 'Chuyển đổi tiền tệ được áp dụng nếu tiền tệ tài khoản của bạn khác với tài sản. Rút tiền tốn $5 cho tài khoản USD (miễn phí cho GBP/EUR). Có phí không hoạt động $10/tháng sau 12 tháng không đăng nhập.',
            'spread_table_title': 'Bảng spread eToro đầy đủ',
            'table_headers': {'asset': 'Loại tài sản', 'spread': 'Spread thông thường', 'commission': 'Hoa hồng', 'overnight': 'Phí qua đêm'},
            'table_rows': {'stocks_us': 'Cổ phiếu (Mỹ)', 'stocks_eu': 'Cổ phiếu (EU/UK)', 'other_crypto': 'Tiền điện tử khác', 'gold': 'Vàng', 'oil': 'Dầu', 'none_crypto': 'Không (tiền điện tử thực)', 'cfd_only': '(chỉ CFD)'},
            'faq_title': 'Câu hỏi thường gặp',
            'faqs': [
                ('Phí giao dịch của eToro là gì?', 'eToro thu phí chủ yếu thông qua spread (chênh lệch giữa giá mua và bán). Giao dịch cổ phiếu và ETF không có hoa hồng. Tiền điện tử có spread 1%. Forex bắt đầu từ 1 pip. Chi phí bổ sung bao gồm phí qua đêm cho vị thế CFD giữ sau 22:00 giờ UK.'),
                ('eToro có thu phí rút tiền không?', 'Chủ tài khoản USD trả phí rút tiền $5 (rút tối thiểu $30). Chủ tài khoản GBP và EUR có thể rút miễn phí.'),
                ('Có phí ẩn trên eToro không?', 'Chi phí "ẩn" chính là phí qua đêm trên vị thế CFD và phí chuyển đổi tiền tệ nếu tiền tệ tài khoản của bạn khác với tài sản. Cũng có phí không hoạt động $10/tháng sau 12 tháng không đăng nhập. Máy tính này hiển thị tất cả các chi phí một cách minh bạch.'),
                ('Copy trading trên eToro có miễn phí không?', 'Có, không có phí bổ sung khi sử dụng tính năng CopyTrader của eToro. Bạn chỉ trả phí giao dịch tiêu chuẩn cho các vị thế mà trader bạn sao chép mở thay mặt bạn. Mức tối thiểu để sao chép một trader là $200.'),
                ('Giao dịch tiền điện tử trên eToro tốn bao nhiêu?', 'eToro thu spread 1% khi mua tiền điện tử. Không có phí qua đêm khi giữ tiền điện tử thực (không phải CFD). Chuyển tiền điện tử sang ví bên ngoài tốn 2%. Spread được tính khi cả mua và bán.'),
            ],
            'cta_title': 'Sẵn sàng bắt đầu đầu tư?',
            'cta_text': 'Tham gia eToro và truy cập cổ phiếu, tiền điện tử, forex và copy trading. Bắt đầu chỉ với $50.',
            'cta_btn': 'Mở tài khoản eToro &rarr;',
            'risk_warning': '<strong>51% tài khoản nhà đầu tư cá nhân thua lỗ khi giao dịch CFD với nhà cung cấp này.</strong> Bạn nên cân nhắc liệu bạn có đủ khả năng chịu rủi ro cao mất tiền hay không. Đây không phải là lời khuyên tài chính. Vốn có rủi ro. Liên kết đối tác: Tom có thể nhận hoa hồng mà không tốn thêm chi phí cho bạn.',
            'footer_tools': 'Tất cả công cụ',
            'footer_disclaimer': 'Máy tính này chỉ nhằm mục đích thông tin và không phải là lời khuyên tài chính. Ước tính phí có thể không chính xác hoặc đã lỗi thời — luôn xác minh trên trang web chính thức của eToro. SocialTradingVlog không chịu trách nhiệm về tổn thất phát sinh từ việc sử dụng công cụ này. eToro là nền tảng đầu tư đa tài sản. Giá trị đầu tư của bạn có thể tăng hoặc giảm. Vốn của bạn có rủi ro. 51% tài khoản nhà đầu tư cá nhân thua lỗ khi giao dịch CFD với nhà cung cấp này.',
            'unknown': 'Không rõ', 'unavailable': 'Không khả dụng',
            'day_singular': ' ngày', 'free_for': 'Miễn phí cho ',
        },
    },
    'el': {
        'code': 'el', 'name': 'Ελληνικά', 'dir': 'el/calculators',
        'calc_slugs': {'fee': 'fee-calculator', 'roi': 'roi-calculator', 'compare': 'compare-platforms', 'position': 'position-size'},
        'nav_labels': {'fee': 'Υπολογιστής χρεώσεων', 'roi': 'Υπολογιστής απόδοσης', 'compare': 'Σύγκριση πλατφορμών'},
        'back_text': '&larr; Πίσω στον ιστότοπο',
        'fee': {
            'title': 'Υπολογιστής χρεώσεων eToro 2026 — Υπολογίστε το κόστος συναλλαγών σας | SocialTradingVlog',
            'meta_desc': 'Δωρεάν υπολογιστής χρεώσεων eToro. Μάθετε ακριβώς πόσο θα πληρώσετε σε spread, χρεώσεις overnight, ανάληψη και μετατροπή νομίσματος. Ενημερωμένο για 2026.',
            'h1': 'Υπολογιστής<span class="accent">χρεώσεων eToro</span>',
            'hero_p': 'Μάθετε ακριβώς πόσο θα πληρώσετε πριν κάνετε συναλλαγή. Εισάγετε τα στοιχεία της συναλλαγής σας και λάβετε πλήρη ανάλυση κόστους σε δευτερόλεπτα.',
            'badge': 'Ενημερωμένο Φεβρουάριος 2026',
            'verified_label': 'Δεδομένα επαληθεύτηκαν τελευταία:',
            'verified_note': ' — Ελέγχουμε τις χρεώσεις του eToro κάθε εβδομάδα. Πάντα επαληθεύστε στη',
            'verified_link_text': 'σελίδα επίσημων χρεώσεων',
            'asset_label': 'Τι θα συναλλαχθείτε;',
            'assets': {'stocks': 'Μετοχές', 'crypto': 'Κρυπτονομίσματα', 'forex': 'Forex', 'commodities': 'Εμπορεύματα', 'indices': 'Δείκτες', 'etfs': 'ETF'},
            'amount_label': 'Ποσό συναλλαγής',
            'period_label': 'Πόσο καιρό θα κρατήσετε τη θέση;',
            'periods': {'intraday': 'Ενδοημερήσια', 'week': '1 εβδομάδα', 'month': '1 μήνας', 'year': '1 έτος'},
            'currency_label': 'Νόμισμα λογαριασμού σας',
            'results_label': 'Εκτιμώμενο συνολικό κόστος',
            'pct_suffix': '% της συναλλαγής σας',
            'spread_label': 'Spread', 'spread_note': 'Χρέωση συναλλαγής',
            'overnight_label': 'Χρεώσεις overnight', 'overnight_intraday': 'Ενδοημερήσια',
            'conversion_label': 'Μετατροπή', 'conversion_note': 'Χρέωση νομίσματος',
            'withdrawal_label': 'Ανάληψη', 'withdrawal_note': 'Εάν κάνετε ανάληψη',
            'legend': {'spread': 'Spread', 'overnight': 'Overnight', 'conversion': 'Μετατροπή', 'withdrawal': 'Ανάληψη'},
            'disclaimer_title': 'Σημείωση ακρίβειας δεδομένων',
            'explainer_title': 'Πώς λειτουργούν οι χρεώσεις eToro',
            'spread_card_title': 'Spread', 'spread_card_text': 'Το spread είναι η διαφορά μεταξύ τιμής αγοράς και πώλησης. Είναι η κύρια πηγή εσόδων του eToro. Μετοχές και ETF χωρίς προμήθεια — πληρώνετε μόνο το spread. Τα spread κρυπτονομισμάτων ξεκινούν από 1%.',
            'overnight_card_title': 'Χρεώσεις overnight', 'overnight_card_text': 'Οι θέσεις CFD που κρατούνται μετά τις 22:00 (ώρα UK) επιβαρύνονται με ημερήσιες χρεώσεις overnight. Αυτά τα κόστη συσσωρεύονται — μια θέση που κρατείται για ένα χρόνο κοστίζει σημαντικά περισσότερο από μια ενδοημερήσια συναλλαγή. Οι θέσεις σε πραγματικά κρυπτονομίσματα και μετοχές εξαιρούνται.',
            'other_card_title': 'Άλλες χρεώσεις', 'other_card_text': 'Η μετατροπή νομίσματος εφαρμόζεται αν το νόμισμα του λογαριασμού σας διαφέρει από το περιουσιακό στοιχείο. Η ανάληψη κοστίζει $5 για λογαριασμούς USD (δωρεάν για GBP/EUR). Υπάρχει χρέωση αδράνειας $10/μήνα μετά από 12 μήνες χωρίς σύνδεση.',
            'spread_table_title': 'Πλήρης πίνακας spread eToro',
            'table_headers': {'asset': 'Κατηγορία περιουσιακού στοιχείου', 'spread': 'Τυπικό spread', 'commission': 'Προμήθεια', 'overnight': 'Χρέωση overnight'},
            'table_rows': {'stocks_us': 'Μετοχές (ΗΠΑ)', 'stocks_eu': 'Μετοχές (EU/UK)', 'other_crypto': 'Άλλα κρυπτονομίσματα', 'gold': 'Χρυσός', 'oil': 'Πετρέλαιο', 'none_crypto': 'Καμία (πραγματικό κρυπτο)', 'cfd_only': '(μόνο CFD)'},
            'faq_title': 'Συχνές ερωτήσεις',
            'faqs': [
                ('Ποιες είναι οι χρεώσεις συναλλαγών του eToro;', 'Το eToro χρεώνει κυρίως μέσω spread (η διαφορά μεταξύ τιμής αγοράς και πώλησης). Οι συναλλαγές μετοχών και ETF είναι χωρίς προμήθεια. Τα κρυπτονομίσματα έχουν spread 1%. Το forex ξεκινά από 1 pip. Τα πρόσθετα κόστη περιλαμβάνουν χρεώσεις overnight για θέσεις CFD που κρατούνται μετά τις 22:00 ώρα UK.'),
                ('Χρεώνει το eToro τέλη ανάληψης;', 'Οι κάτοχοι λογαριασμών USD πληρώνουν τέλος ανάληψης $5 (ελάχιστη ανάληψη $30). Οι κάτοχοι λογαριασμών GBP και EUR μπορούν να κάνουν ανάληψη δωρεάν.'),
                ('Υπάρχουν κρυφές χρεώσεις στο eToro;', 'Τα κύρια «κρυφά» κόστη είναι οι χρεώσεις overnight σε θέσεις CFD και οι χρεώσεις μετατροπής νομίσματος αν το νόμισμα του λογαριασμού σας διαφέρει από το περιουσιακό στοιχείο. Υπάρχει επίσης χρέωση αδράνειας $10/μήνα μετά από 12 μήνες χωρίς σύνδεση. Αυτός ο υπολογιστής δείχνει όλα τα κόστη με διαφάνεια.'),
                ('Είναι δωρεάν το copy trading στο eToro;', 'Ναι, δεν υπάρχουν επιπλέον χρεώσεις για τη χρήση της λειτουργίας CopyTrader του eToro. Πληρώνετε μόνο τις τυπικές χρεώσεις συναλλαγών για τις θέσεις που ανοίγει ο trader που αντιγράφετε εκ μέρους σας. Το ελάχιστο για να αντιγράψετε έναν trader είναι $200.'),
                ('Πόσο κοστίζει η συναλλαγή κρυπτονομισμάτων στο eToro;', 'Το eToro χρεώνει spread 1% στην αγορά κρυπτονομισμάτων. Δεν υπάρχουν χρεώσεις overnight για τη διατήρηση πραγματικών κρυπτονομισμάτων (όχι CFD). Η μεταφορά κρυπτονομισμάτων σε εξωτερικό πορτοφόλι κοστίζει 2%. Το spread χρεώνεται τόσο κατά την αγορά όσο και κατά την πώληση.'),
            ],
            'cta_title': 'Έτοιμοι να ξεκινήσετε να επενδύετε;',
            'cta_text': 'Εγγραφείτε στο eToro και αποκτήστε πρόσβαση σε μετοχές, κρυπτονομίσματα, forex και copy trading. Ξεκινήστε με μόλις $50.',
            'cta_btn': 'Άνοιγμα λογαριασμού eToro &rarr;',
            'risk_warning': '<strong>Το 51% των λογαριασμών ιδιωτών επενδυτών χάνουν χρήματα κατά τη διαπραγμάτευση CFD με αυτόν τον πάροχο.</strong> Θα πρέπει να εξετάσετε αν μπορείτε να αντέξετε τον υψηλό κίνδυνο απώλειας των χρημάτων σας. Αυτή δεν είναι οικονομική συμβουλή. Το κεφάλαιο κινδυνεύει. Σύνδεσμος συνεργάτη: Ο Tom μπορεί να λάβει προμήθεια χωρίς επιπλέον κόστος για εσάς.',
            'footer_tools': 'Όλα τα εργαλεία',
            'footer_disclaimer': 'Αυτός ο υπολογιστής είναι μόνο για ενημερωτικούς σκοπούς και δεν αποτελεί οικονομική συμβουλή. Οι εκτιμήσεις χρεώσεων μπορεί να είναι ανακριβείς ή παρωχημένες — πάντα επαληθεύστε στην επίσημη ιστοσελίδα του eToro. Το SocialTradingVlog δεν ευθύνεται για απώλειες που προκύπτουν από τη χρήση αυτού του εργαλείου. Το eToro είναι πλατφόρμα επενδύσεων πολλαπλών περιουσιακών στοιχείων. Η αξία των επενδύσεών σας μπορεί να αυξηθεί ή να μειωθεί. Το κεφάλαιό σας κινδυνεύει. Το 51% των λογαριασμών ιδιωτών επενδυτών χάνουν χρήματα κατά τη διαπραγμάτευση CFD με αυτόν τον πάροχο.',
            'unknown': 'Άγνωστο', 'unavailable': 'Μη διαθέσιμο',
            'day_singular': ' ημέρες', 'free_for': 'Δωρεάν για ',
        },
    },
    'cs': {
        'code': 'cs', 'name': 'Čeština', 'dir': 'cs/kalkulacky',
        'calc_slugs': {'fee': 'kalkulacka-poplatku', 'roi': 'kalkulacka-vynosu', 'compare': 'porovnani-platforem', 'position': 'velikost-pozice'},
        'nav_labels': {'fee': 'Kalkulačka poplatků', 'roi': 'Kalkulačka výnosů', 'compare': 'Porovnání platforem'},
        'back_text': '&larr; Zpět na web',
        'fee': {
            'title': 'Kalkulačka poplatků eToro 2026 — Spočítejte si náklady na obchodování | SocialTradingVlog',
            'meta_desc': 'Bezplatná kalkulačka poplatků eToro. Zjistěte přesně, kolik zaplatíte za spready, poplatky přes noc, výběry a konverze měn. Aktualizováno pro 2026.',
            'h1': 'Kalkulačka<span class="accent">poplatků eToro</span>',
            'hero_p': 'Zjistěte přesně, kolik zaplatíte, než začnete obchodovat. Zadejte podrobnosti svého obchodu a získejte kompletní rozpis nákladů během několika sekund.',
            'badge': 'Aktualizováno únor 2026',
            'verified_label': 'Data naposledy ověřena:',
            'verified_note': ' — Kontrolujeme poplatky eToro každý týden. Vždy si ověřte na',
            'verified_link_text': 'oficiální stránce poplatků',
            'asset_label': 'Co budete obchodovat?',
            'assets': {'stocks': 'Akcie', 'crypto': 'Kryptoměny', 'forex': 'Forex', 'commodities': 'Komodity', 'indices': 'Indexy', 'etfs': 'ETF'},
            'amount_label': 'Částka obchodu',
            'period_label': 'Jak dlouho budete pozici držet?',
            'periods': {'intraday': 'Intradenní', 'week': '1 týden', 'month': '1 měsíc', 'year': '1 rok'},
            'currency_label': 'Měna vašeho účtu',
            'results_label': 'Odhadované celkové náklady',
            'pct_suffix': '% vašeho obchodu',
            'spread_label': 'Spread', 'spread_note': 'Poplatek za obchod',
            'overnight_label': 'Poplatky přes noc', 'overnight_intraday': 'Intradenní',
            'conversion_label': 'Konverze', 'conversion_note': 'Poplatek za měnu',
            'withdrawal_label': 'Výběr', 'withdrawal_note': 'Pokud vybíráte prostředky',
            'legend': {'spread': 'Spread', 'overnight': 'Přes noc', 'conversion': 'Konverze', 'withdrawal': 'Výběr'},
            'disclaimer_title': 'Upozornění na přesnost dat',
            'explainer_title': 'Jak fungují poplatky eToro',
            'spread_card_title': 'Spready', 'spread_card_text': 'Spread je rozdíl mezi nákupní a prodejní cenou. Je hlavním zdrojem příjmů eToro. Akcie a ETF bez provize — platíte pouze spread. Spready kryptoměn začínají na 1 %.',
            'overnight_card_title': 'Poplatky přes noc', 'overnight_card_text': 'CFD pozice držené po 22:00 (UK čas) podléhají denním poplatkům přes noc. Tyto náklady se kumulují — pozice držená jeden rok stojí výrazně více než intradenní obchod. Pozice v reálných kryptoměnách a akciích jsou osvobozeny.',
            'other_card_title': 'Ostatní poplatky', 'other_card_text': 'Konverze měny se účtuje, pokud se měna vašeho účtu liší od aktiva. Výběr stojí 5 $ pro účty v USD (zdarma pro GBP/EUR). Po 12 měsících neaktivity se účtuje poplatek 10 $/měsíc.',
            'spread_table_title': 'Kompletní tabulka spreadů eToro',
            'table_headers': {'asset': 'Třída aktiv', 'spread': 'Typický spread', 'commission': 'Provize', 'overnight': 'Poplatek přes noc'},
            'table_rows': {'stocks_us': 'Akcie (USA)', 'stocks_eu': 'Akcie (EU/UK)', 'other_crypto': 'Ostatní kryptoměny', 'gold': 'Zlato', 'oil': 'Ropa', 'none_crypto': 'Žádný (reálné krypto)', 'cfd_only': '(pouze CFD)'},
            'faq_title': 'Často kladené otázky',
            'faqs': [
                ('Jaké jsou poplatky za obchodování na eToro?', 'eToro účtuje poplatky především prostřednictvím spreadů (rozdíl mezi nákupní a prodejní cenou). Obchody s akciemi a ETF jsou bez provize. Kryptoměny mají spread 1 %. Forex začíná na 1 pipu. Další náklady zahrnují poplatky přes noc pro CFD pozice držené po 22:00 UK času.'),
                ('Účtuje eToro poplatky za výběr?', 'Majitelé účtů v USD platí poplatek za výběr 5 $ (minimální výběr 30 $). Majitelé účtů v GBP a EUR mohou vybírat zdarma.'),
                ('Existují na eToro skryté poplatky?', 'Hlavní „skryté" náklady jsou poplatky přes noc u CFD pozic a poplatky za konverzi měn, pokud se měna vašeho účtu liší od aktiva. Existuje také poplatek za neaktivitu 10 $/měsíc po 12 měsících bez přihlášení. Tato kalkulačka zobrazuje všechny náklady transparentně.'),
                ('Je copy trading na eToro zdarma?', 'Ano, za používání funkce CopyTrader na eToro nejsou žádné další poplatky. Platíte pouze standardní obchodní poplatky za pozice, které obchodník, kterého kopírujete, otevře vaším jménem. Minimum pro kopírování obchodníka je 200 $.'),
                ('Kolik stojí obchodování kryptoměn na eToro?', 'eToro účtuje spread 1 % při nákupu kryptoměn. Za držení reálných kryptoměn (nikoliv CFD) nejsou žádné poplatky přes noc. Převod kryptoměn na externí peněženku stojí 2 %. Spread se účtuje při nákupu i prodeji.'),
            ],
            'cta_title': 'Připraveni začít investovat?',
            'cta_text': 'Připojte se k eToro a získejte přístup k akciím, kryptoměnám, forexu a copy tradingu. Začněte s pouhými 50 $.',
            'cta_btn': 'Otevřít účet eToro &rarr;',
            'risk_warning': '<strong>51 % účtů retailových investorů ztrácí peníze při obchodování CFD s tímto poskytovatelem.</strong> Měli byste zvážit, zda si můžete dovolit vysoké riziko ztráty svých peněz. Toto není finanční porada. Kapitál je v ohrožení. Affiliate odkaz: Tom může obdržet provizi bez dalších nákladů pro vás.',
            'footer_tools': 'Všechny nástroje',
            'footer_disclaimer': 'Tato kalkulačka slouží pouze k informačním účelům a nepředstavuje finanční poradenství. Odhady poplatků mohou být nepřesné nebo zastaralé — vždy si ověřte na oficiálních stránkách eToro. SocialTradingVlog nenese odpovědnost za ztráty vzniklé použitím tohoto nástroje. eToro je investiční platforma s více aktivy. Hodnota vašich investic může stoupat nebo klesat. Váš kapitál je v ohrožení. 51 % účtů retailových investorů ztrácí peníze při obchodování CFD s tímto poskytovatelem.',
            'unknown': 'Neznámé', 'unavailable': 'Nedostupné',
            'day_singular': ' dní', 'free_for': 'Zdarma pro ',
        },
    },
}

def generate_fee_calc(lang_code, lang_config):
    """Generate a fee calculator page by adapting the Thai template."""
    # Read Thai template
    with open(os.path.join(BASE, 'th/calculators/fee-calculator/index.html'), 'r') as f:
        content = f.read()

    fee = lang_config['fee']
    slugs = lang_config['calc_slugs']
    code = lang_config['code']
    calc_dir = lang_config['dir']

    # Replace lang attribute
    content = content.replace('lang="th"', f'lang="{code}"')

    # Replace canonical
    if code == 'el':
        new_canonical = f'https://socialtradingvlog.com/{code}/calculators/{slugs["fee"]}/'
    else:
        new_canonical = f'https://socialtradingvlog.com/{calc_dir}/{slugs["fee"]}/'
    content = content.replace(
        'https://socialtradingvlog.com/th/calculators/fee-calculator/',
        new_canonical
    )

    # Replace title
    content = content.replace(
        'เครื่องคำนวณค่าธรรมเนียม eToro 2026 — คำนวณต้นทุนการเทรดของคุณ | SocialTradingVlog',
        fee['title']
    )

    # Replace meta description
    content = content.replace(
        'เครื่องคำนวณค่าธรรมเนียม eToro ฟรี ดูค่าใช้จ่ายที่แน่นอนสำหรับสเปรด ค่าธรรมเนียมข้ามคืน ค่าถอนเงิน และการแปลงสกุลเงิน อัปเดตสำหรับ 2026',
        fee['meta_desc']
    )

    # Replace OG title/description
    content = content.replace(
        'เครื่องคำนวณค่าธรรมเนียม eToro 2026 — คำนวณต้นทุนการเทรดของคุณ',
        fee['title'].replace(' | SocialTradingVlog', '')
    )
    content = content.replace(
        'เครื่องคำนวณค่าธรรมเนียม eToro ฟรี ดูค่าใช้จ่ายที่แน่นอนสำหรับสเปรด ค่าธรรมเนียมข้ามคืน และอื่นๆ',
        fee['meta_desc'][:150]
    )

    # Replace OG URL
    content = content.replace(
        '"og:url" content="https://socialtradingvlog.com/th/calculators/fee-calculator/"',
        f'"og:url" content="{new_canonical}"'
    )

    # Replace keywords
    content = re.sub(r'<meta name="keywords"[^>]*>', f'<meta name="keywords" content="{code} etoro fees calculator">', content)

    # Replace nav links
    content = content.replace('../fee-calculator/', f'../{slugs["fee"]}/')
    content = content.replace('../roi-calculator/', f'../{slugs["roi"]}/')
    content = content.replace('../compare-platforms/', f'../{slugs["compare"]}/')

    # Replace nav labels
    nav = lang_config['nav_labels']
    content = content.replace('>คำนวณค่าธรรมเนียม</a>', f'>{nav["fee"]}</a>')
    content = content.replace('>คำนวณผลตอบแทน</a>', f'>{nav["roi"]}</a>')
    content = content.replace('>เปรียบเทียบแพลตฟอร์ม</a>', f'>{nav["compare"]}</a>')

    # Replace back link
    content = content.replace('../../../th/', f'../../../{code}/')
    content = content.replace('กลับสู่เว็บไซต์', lang_config['back_text'].replace('&larr; ', ''))

    # Replace hero content
    content = content.replace('อัปเดตเมื่อกุมภาพันธ์ 2026', fee['badge'])
    content = content.replace('เครื่องคำนวณ<span class="accent">ค่าธรรมเนียม eToro</span>', fee['h1'])
    content = content.replace('ค้นหาว่าคุณจะจ่ายเท่าไหร่ก่อนเทรด กรอกรายละเอียดการเทรดของคุณแล้วรับรายละเอียดต้นทุนทั้งหมดในไม่กี่วินาที', fee['hero_p'])

    # Replace verified banner
    content = content.replace('ตรวจสอบข้อมูลล่าสุดเมื่อ:', fee['verified_label'])
    content = content.replace('กำลังโหลด...', fee.get('loading', 'Loading...'))
    content = content.replace(' — เราตรวจสอบค่าธรรมเนียม eToro ทุกสัปดาห์ กรุณาตรวจสอบที่', fee['verified_note'])
    content = content.replace('หน้าค่าธรรมเนียมอย่างเป็นทางการ', fee['verified_link_text'])
    content = content.replace('ก่อนเทรดเสมอ', '')

    # Replace input labels
    content = content.replace('คุณจะเทรดอะไร?', fee['asset_label'])
    content = content.replace('>หุ้น</button>', f'>{fee["assets"]["stocks"]}</button>')
    content = content.replace('>คริปโต</button>', f'>{fee["assets"]["crypto"]}</button>')
    content = content.replace('>ฟอเร็กซ์</button>', f'>{fee["assets"]["forex"]}</button>')
    content = content.replace('>สินค้าโภคภัณฑ์</button>', f'>{fee["assets"]["commodities"]}</button>')
    content = content.replace('>ดัชนี</button>', f'>{fee["assets"]["indices"]}</button>')
    # ETFs stays as ETFs

    content = content.replace('จำนวนเงินที่เทรด', fee['amount_label'])
    content = content.replace('คุณจะถือตำแหน่งนานแค่ไหน?', fee['period_label'])
    content = content.replace('>ภายในวัน</button>', f'>{fee["periods"]["intraday"]}</button>')
    content = content.replace('>1 สัปดาห์</button>', f'>{fee["periods"]["week"]}</button>')
    content = content.replace('>1 เดือน</button>', f'>{fee["periods"]["month"]}</button>')
    content = content.replace('>1 ปี</button>', f'>{fee["periods"]["year"]}</button>')
    content = content.replace('สกุลเงินในบัญชีของคุณ', fee['currency_label'])

    # Replace results labels
    content = content.replace('ต้นทุนรวมโดยประมาณ', fee['results_label'])
    content = content.replace('>สเปรด</div>', f'>{fee["spread_label"]}</div>', 1)
    content = content.replace('ค่าธรรมเนียมการเทรด', fee['spread_note'])
    content = content.replace('>ค่าธรรมเนียมข้ามคืน</div>', f'>{fee["overnight_label"]}</div>')
    content = content.replace('>การแปลงสกุลเงิน</div>', f'>{fee["conversion_label"]}</div>')
    content = content.replace('ค่าธรรมเนียมสกุลเงิน', fee['conversion_note'])
    content = content.replace('>ถอนเงิน</div>', f'>{fee["withdrawal_label"]}</div>')
    content = content.replace('หากคุณถอนเงิน', fee['withdrawal_note'])

    # Legend
    for th_text, key in [('สเปรด', 'spread'), ('ข้ามคืน', 'overnight'), ('แปลงสกุลเงิน', 'conversion'), ('ถอนเงิน', 'withdrawal')]:
        content = content.replace(f'</span>{th_text}</span>', f'</span>{fee["legend"][key]}</span>')

    # Replace JS strings
    content = content.replace("label: 'หุ้น'", f"label: '{fee['assets']['stocks']}'")
    content = content.replace("label: 'คริปโต'", f"label: '{fee['assets']['crypto']}'")
    content = content.replace("label: 'ฟอเร็กซ์'", f"label: '{fee['assets']['forex']}'")
    content = content.replace("label: 'สินค้าโภคภัณฑ์'", f"label: '{fee['assets']['commodities']}'")
    content = content.replace("label: 'ดัชนี'", f"label: '{fee['assets']['indices']}'")

    content = content.replace("stocks: 'หุ้น'", f"stocks: '{fee['assets']['stocks']}'")
    content = content.replace("crypto: 'คริปโต'", f"crypto: '{fee['assets']['crypto']}'")
    content = content.replace("forex: 'ฟอเร็กซ์'", f"forex: '{fee['assets']['forex']}'")
    content = content.replace("commodities: 'สินค้าโภคภัณฑ์'", f"commodities: '{fee['assets']['commodities']}'")
    content = content.replace("indices: 'ดัชนี'", f"indices: '{fee['assets']['indices']}'")

    content = content.replace("'ไม่ทราบ'", f"'{fee['unknown']}'")
    content = content.replace("'ไม่พร้อมใช้งาน'", f"'{fee['unavailable']}'")

    # Replace JS display strings
    content = content.replace("'% ของการเทรดของคุณ'", f"'{fee['pct_suffix']}'")
    content = content.replace("? 'ภายในวัน'", f"? '{fee['overnight_intraday']}'")
    content = content.replace("+ ' วัน'", f"+ '{fee['day_singular']}'")
    content = content.replace("'ฟรีสำหรับ '", f"'{fee['free_for']}'")
    content = content.replace("'หากคุณถอนเงิน'", f"'{fee['withdrawal_note']}'")

    # Replace explainer section
    content = content.replace('ค่าธรรมเนียม eToro ทำงานอย่างไร', fee['explainer_title'])
    content = content.replace('>สเปรด</h3>', f'>{fee["spread_card_title"]}</h3>')
    content = content.replace('สเปรดคือส่วนต่างระหว่างราคาซื้อและราคาขาย เป็นรายได้หลักของ eToro หุ้นและ ETF ไม่มีค่าคอมมิชชัน — คุณจ่ายแค่สเปรด สเปรดคริปโตเริ่มต้นที่ 1%', fee['spread_card_text'])
    content = content.replace('>ค่าธรรมเนียมข้ามคืน</h3>', f'>{fee["overnight_card_title"]}</h3>')
    content = content.replace('>ค่าธรรมเนียมอื่นๆ</h3>', f'>{fee["other_card_title"]}</h3>')

    # Replace spread table
    content = content.replace('ตารางสเปรด eToro ฉบับสมบูรณ์', fee['spread_table_title'])
    content = content.replace('>ประเภทสินทรัพย์</th>', f'>{fee["table_headers"]["asset"]}</th>')
    content = content.replace('>สเปรดทั่วไป</th>', f'>{fee["table_headers"]["spread"]}</th>')
    content = content.replace('>ค่าคอมมิชชัน</th>', f'>{fee["table_headers"]["commission"]}</th>')
    content = content.replace('>ค่าธรรมเนียมข้ามคืน</th>', f'>{fee["table_headers"]["overnight"]}</th>')

    # Replace FAQ
    content = content.replace('คำถามที่พบบ่อย', fee['faq_title'])

    # Replace CTA
    content = content.replace('พร้อมเริ่มลงทุนหรือยัง?', fee['cta_title'])
    content = content.replace('เข้าร่วม eToro และเข้าถึงหุ้น คริปโต ฟอเร็กซ์ และ Copy Trading เริ่มต้นด้วยเงินเพียง $50', fee['cta_text'])
    content = content.replace('เปิดบัญชี eToro &rarr;', fee['cta_btn'])
    content = content.replace("event_label:'fee_calculator_th'", f"event_label:'fee_calculator_{code}'")

    # Replace footer
    content = content.replace('>เครื่องมือทั้งหมด</a>', f'>{fee["footer_tools"]}</a>')

    # Replace inLanguage in schema
    content = content.replace('"inLanguage": "th"', f'"inLanguage": "{code}"')
    content = content.replace('"name": "Th"', f'"name": "{lang_config["name"]}"')

    # Replace schema breadcrumb URLs
    content = content.replace('"item": "https://socialtradingvlog.com/th/"', f'"item": "https://socialtradingvlog.com/{code}/"')
    content = content.replace('"item": "https://socialtradingvlog.com/th/calculators/"', f'"item": "https://socialtradingvlog.com/{calc_dir}/"')
    content = content.replace('"item": "https://socialtradingvlog.com/th/calculators/fee-calculator/"', f'"item": "{new_canonical}"')

    # Write
    out_path = os.path.join(BASE, calc_dir, slugs['fee'], 'index.html')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        f.write(content)
    print(f"  Created: {out_path} ({len(content.splitlines())} lines)")


def copy_and_adapt(src_path, dest_path, src_lang, dest_lang, dest_config):
    """Copy a calculator page from one language to another, adapting URLs and lang code."""
    with open(src_path, 'r') as f:
        content = f.read()

    code = dest_config['code']

    # Replace lang attribute
    content = content.replace(f'lang="{src_lang}"', f'lang="{code}"')
    content = content.replace(f'"inLanguage": "{src_lang}"', f'"inLanguage": "{code}"')

    # Replace language root URLs
    content = content.replace(f'../../../{src_lang}/', f'../../../{code}/')

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, 'w') as f:
        f.write(content)
    print(f"  Created: {dest_path} ({len(content.splitlines())} lines)")


# Check what's missing
missing = {}
for lang_code, config in LANGS.items():
    calc_dir = config['dir']
    slugs = config['calc_slugs']
    for calc_type, slug in slugs.items():
        path = os.path.join(BASE, calc_dir, slug, 'index.html')
        if not os.path.exists(path):
            missing.setdefault(lang_code, []).append(calc_type)

print("Missing calculator pages:")
for lang, types in missing.items():
    print(f"  {lang}: {', '.join(types)}")

print("\nGenerating fee calculator pages...")
for lang_code, config in LANGS.items():
    slug = config['calc_slugs']['fee']
    path = os.path.join(BASE, config['dir'], slug, 'index.html')
    if not os.path.exists(path):
        print(f"\n  Generating {lang_code} fee calculator...")
        generate_fee_calc(lang_code, config)

print("\nDone with fee calculators!")
print(f"\nRemaining pages to create manually: ROI, compare, position-size for {list(missing.keys())}")
