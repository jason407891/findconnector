//共同頁面相關

// 取得目前登入 token（支援舊 key 與新 key）
function getToken() {
    const token = localStorage.getItem('auth_token') || localStorage.getItem('token');
    return token === 'null' || !token ? null : token;
}

// HEADER 跟 FOOTER
function loadHeaderFooter(){
    let headerhtml=`
        <div class="user">
            <div class="user-logout"></div>
            <img src="../static/user.png" class="user-icon" onmouseover="style.opacity=0.7" onmouseout="style.opacity=1" onclick="handle_account('login')"></img>
        </div>
        <hr>
        <div class="search">
            <div class="logo">
                <a href="/" class="index_title">FINDCONNECTOR</a>
            </div>
            <div class="search_bar">
                <div class="search_text">產品編號</div>
                <input placeholder="請輸入產品編號" class="search-bar"></input>
                <div class="search_btn" onclick="search()">搜尋</div>    
            </div>
            <div class="search_select">
                <div class="checkboxes">
                    <label><input type="checkbox" class="factory_stock">工廠庫存</label>
                    <label><input type="checkbox" class="agent_stock">代理商庫存(開發中)</label>
                </div> 
            </div>
        </div>
        <hr>
        <div class="functionlist">
            <div class="brand">製造商</div>
            <div class="uploadstock">上傳庫存</div>
            <div class="bomservice">BOM服務</div>
            <div class="contact">聯繫我們</div>
        </div>
        <hr>
        `;

    let footerhtml=`
        <div class="about" onclick="showalert()">關於我們</div>
        <div class="faq">常見問題</div>
        <div class="introduction">網站介紹</div>
    `;
    let header=document.getElementsByClassName("header")[0];
    let footer=document.getElementsByClassName("footer")[0];
    header.innerHTML=headerhtml;
    footer.innerHTML=footerhtml;
}

function initChatWidget() {
    // 若在 chat 頁面就不顯示浮動按鈕（chat 頁面留給客服人員）
    if (window.location.pathname === '/chat') return;

    const style = document.createElement('style');
    style.textContent = `
        #chatWidget {
            position: fixed;
            right: 20px;
            bottom: 20px;
            z-index: 9999;
        }
        #chatWidget button {
            background-color: #007bff;
            border: none;
            color: white;
            padding: 12px 16px;
            border-radius: 24px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            cursor: pointer;
            font-weight: 700;
            font-size: 14px;
        }
        #chatWidget button:hover {
            background-color: #0056b3;
        }

        #chatWidget .badge {
            position: absolute;
            top: -6px;
            right: -6px;
            min-width: 18px;
            height: 18px;
            padding: 0 6px;
            border-radius: 999px;
            background: #ff4d4f;
            color: #fff;
            font-size: 12px;
            line-height: 18px;
            text-align: center;
            display: none;
        }

        /* 聊天浮窗 */
        #chatWidgetModal {
            position: fixed;
            right: 20px;
            bottom: 20px;
            width: 360px;
            height: 520px;
            background: transparent;
            display: none;
            z-index: 10000;
            font-family: inherit;
        }
        #chatWidgetModal.show {
            display: block;
        }
        #chatWidgetModal .chat-panel {
            width: 100%;
            height: 100%;
            background: #fff;
            border-radius: 16px;
            box-shadow: 0 10px 28px rgba(0, 0, 0, 0.25);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        #chatWidgetModal .chat-panel-header {
            padding: 12px 14px;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        #chatWidgetModal .chat-panel-title {
            font-size: 15px;
            font-weight: 700;
            color: #222;
        }
        #chatWidgetModal .chat-panel-close {
            border: none;
            background: transparent;
            font-size: 22px;
            cursor: pointer;
            color: #666;
            line-height: 1;
        }
        #chatWidgetModal .chat-panel-messages {
            flex: 1;
            padding: 12px;
            overflow-y: auto;
            background: #f7f8fb;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        #chatWidgetModal .message {
            max-width: 80%;
            padding: 10px 12px;
            border-radius: 14px;
            line-height: 1.4;
            word-break: break-word;
        }
        #chatWidgetModal .message.user {
            align-self: flex-end;
            background: #007bff;
            color: #fff;
            border-bottom-right-radius: 4px;
        }
        #chatWidgetModal .message.agent {
            align-self: flex-start;
            background: #e0e0e0;
            color: #333;
            border-bottom-left-radius: 4px;
        }
        #chatWidgetModal .message-time {
            font-size: 11px;
            color: #666;
            margin-top: 4px;
        }
        #chatWidgetModal .chat-panel-input {
            padding: 10px;
            border-top: 1px solid #e0e0e0;
            display: flex;
            gap: 8px;
            align-items: flex-end;
        }
        #chatWidgetModal .chat-panel-input textarea {
            flex: 1;
            resize: none;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 10px;
            font-family: inherit;
            font-size: 13px;
        }
        #chatWidgetModal .chat-panel-input button {
            padding: 10px 16px;
            border: none;
            border-radius: 10px;
            background: #007bff;
            color: #fff;
            cursor: pointer;
        }
        #chatWidgetModal .chat-panel-input button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
    `;
    document.head.appendChild(style);

    const widget = document.createElement('div');
    widget.id = 'chatWidget';
    widget.style.position = 'relative';

    const button = document.createElement('button');
    button.textContent = '客服聊天';
    button.addEventListener('click', () => {
        const token = getToken();
        if (!token) {
            handle_account('login');
            return;
        }
        openChatWidgetModal();
    });

    const badge = document.createElement('span');
    badge.className = 'badge';
    badge.id = 'chatWidgetBadge';
    widget.appendChild(button);
    widget.appendChild(badge);

    document.body.appendChild(widget);

    createChatWidgetModal();
    updateChatWidgetBadge();
    setInterval(updateChatWidgetBadge, 10000); // 每 10 秒更新未讀數
}

function updateChatWidgetBadge() {
    const token = getToken();
    if (!token) return;

    fetch(`${API_BASE_URL}/chat/unread`, {
        method: 'GET',
        headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
    })
    .then(res => res.json())
    .then(data => {
        const badge = document.getElementById('chatWidgetBadge');
        if (!badge) return;

        if (!data.error && data.unread_count && data.unread_count > 0) {
            badge.textContent = data.unread_count > 99 ? '99+' : data.unread_count;
            badge.style.display = 'block';
        } else {
            badge.style.display = 'none';
        }
    })
    .catch(() => {});
}

function createChatWidgetModal() {
    if (document.getElementById('chatWidgetModal')) return;

    const modal = document.createElement('div');
    modal.id = 'chatWidgetModal';

    modal.innerHTML = `
        <div class="chat-panel">
            <div class="chat-panel-header">
                <div class="chat-panel-title">客服聊天</div>
                <button class="chat-panel-close" id="closeChatWidget">×</button>
            </div>
            <div class="chat-panel-messages" id="chatMessages">
                <div style="color: #999; padding: 16px;">載入對話中...</div>
            </div>
            <div class="chat-panel-input">
                <textarea id="chatInput" placeholder="輸入訊息…" rows="2"></textarea>
                <button id="chatSendBtn" disabled>發送</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    document.getElementById('closeChatWidget').addEventListener('click', closeChatWidgetModal);
    document.getElementById('chatSendBtn').addEventListener('click', sendChatWidgetMessage);
    document.getElementById('chatInput').addEventListener('input', () => {
        const btn = document.getElementById('chatSendBtn');
        btn.disabled = !document.getElementById('chatInput').value.trim();
    });
}

let chatWidgetCurrentConversationId = null;

function openChatWidgetModal() {
    const token = getToken();
    if (!token) {
        handle_account('login');
        return;
    }

    const modal = document.getElementById('chatWidgetModal');
    if (!modal) return;

    modal.classList.add('show');
    document.getElementById('chatMessages').innerHTML = '<div style="color: #999; padding: 16px;">載入對話中...</div>';
    document.getElementById('chatInput').value = '';
    document.getElementById('chatSendBtn').disabled = true;

    ensureChatConversation();
    updateChatWidgetBadge();
}

function closeChatWidgetModal() {
    const modal = document.getElementById('chatWidgetModal');
    if (!modal) return;
    modal.classList.remove('show');
}

function ensureChatConversation() {
    const token = getToken();
    if (!token) return;

    // 先嘗試拿最新對話；沒有就建立一個
    fetch(`${API_BASE_URL}/chat/conversations`, {
        method: 'GET',
        headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
    })
    .then(res => res.json())
    .then(data => {
        if (!data.error && data.conversations && data.conversations.length) {
            chatWidgetCurrentConversationId = data.conversations[0].id;
            return loadChatWidgetHistory(chatWidgetCurrentConversationId);
        }

        return fetch(`${API_BASE_URL}/chat/start`, {
            method: 'POST',
            headers: {
                'Authorization': token,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ subject: '客服聊天' })
        });
    })
    .then(res => {
        if (!res) return;
        return res.json();
    })
    .then(data => {
        if (!data || data.error) return;
        chatWidgetCurrentConversationId = data.conversation_id;
        loadChatWidgetHistory(chatWidgetCurrentConversationId);
    })
    .catch(() => {
        document.getElementById('chatMessages').innerHTML = '<div style="color: #d33; padding: 16px;">讀取對話失敗，請稍後再試。</div>';
    });
}

function loadChatWidgetHistory(conversationId) {
    const token = getToken();
    const container = document.getElementById('chatMessages');
    container.innerHTML = '<div style="color: #666; padding: 16px;">載入中…</div>';

    fetch(`${API_BASE_URL}/chat/conversation/${conversationId}`, {
        method: 'GET',
        headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            container.innerHTML = '<div style="padding: 16px; color: #d33;">讀取失敗</div>';
            return;
        }

        if (!data.messages || !data.messages.length) {
            container.innerHTML = '<div style="padding: 16px; color: #666;">目前還沒有訊息。</div>';
            return;
        }

        container.innerHTML = data.messages.map(msg => {
            const cls = msg.message_type === 'user' ? 'user' : 'agent';
            const label = msg.message_type === 'user' ? '您' : '客服';
            return `
                <div class="message ${cls}">
                    <div>${escapeHtml(msg.message)}</div>
                    <div class="message-time">${label} • ${formatTime(msg.created_at)}</div>
                </div>
            `;
        }).join('');

        container.scrollTop = container.scrollHeight;
    })
    .catch(() => {
        container.innerHTML = '<div style="padding: 16px; color: #d33;">讀取失敗</div>';
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' });
}

function sendChatWidgetMessage() {
    const token = getToken();
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    const sendBtn = document.getElementById('chatSendBtn');

    if (!message || !chatWidgetCurrentConversationId) return;

    sendBtn.disabled = true;
    sendBtn.textContent = '發送中…';

    fetch(`${API_BASE_URL}/chat/send`, {
        method: 'POST',
        headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            conversation_id: chatWidgetCurrentConversationId,
            message: message,
            type: 'user'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (!data.error) {
            input.value = '';
            sendBtn.disabled = true;
            loadChatWidgetHistory(chatWidgetCurrentConversationId);
        }
    })
    .catch(() => {})
    .finally(() => {
        sendBtn.disabled = !input.value.trim();
        sendBtn.textContent = '發送';
    });
}

window.addEventListener("load", () => {
    loadHeaderFooter();
    initChatWidget();
});


//帳號登入跟註冊的頁面內容
function loadAccount(){
    let accounthtml=`
    <div class="signup_block">
            <div class="signup">
                <div class="deco_bar"></div>
                <div class="signup_text">註冊會員帳戶</div>
                <img src="../static/close.png" class="close_button" onclick="handle_account('close')"></img>
                <input class="register_input" name="name" placeholder="會員姓名">
                <input class="register_input" name="email" placeholder="電子郵件">
                <input class="register_input" name="password" placeholder="密碼" type="password">
                <input class="register_input" name="company_name" placeholder="公司名稱">
                <input class="register_input" name="phone_number" placeholder="聯繫電話">
                <input class="register_input" name="address" placeholder="倉庫地址">
                <input class="submit_btn" onclick="register()" value="註冊新帳戶">
                <div class="signup_link"><span id="have_account">已經有帳戶了？</span><span onclick="handle_account('login')">點此登入</span></div>
            </div>
        </div>
        <div class="login_block">
            <div class="login">
                <div class="deco_bar"></div>
                <div class="login_text">登入會員帳戶</div>
                <img src="../static/close.png" class="close_button" onclick="handle_account('close')"></img>
                <input class="login_input" placeholder="輸入電子信箱">
                <input class="login_input" placeholder="輸入密碼" type="password">
                <input class="submit_btn" onclick="login()" value="登入帳戶">
                <div class="login_link">還沒有帳戶？<span onclick="handle_account('register')">點此註冊</span></div>
            </div>
        </div>
    `;
    let account=document.getElementsByClassName("account")[0];
    account.innerHTML=accounthtml;
}
//每個頁面都要自動加載
window.addEventListener("load", loadAccount); 

//控制登入註冊打開關閉
function handle_account(mode){
    let register=document.getElementsByClassName("signup_block")[0];
    let login=document.getElementsByClassName("login_block")[0];
    if (mode=="login"){
        login.style.display="flex";
        register.style.display="none";
    }
    else if (mode=="register"){
        login.style.display="none";
        register.style.display="flex";
    }
    else if (mode=="close"){
        login.style.display="none";
        register.style.display="none";
    }
}



// 處理功能跳轉
function handle_functionlist(){
    let index=document.getElementsByClassName("index_title")[0];
    let brand=document.getElementsByClassName("brand")[0];
    let uploadstock=document.getElementsByClassName("uploadstock")[0];
    let bomservice=document.getElementsByClassName("bomservice")[0];
    let contact=document.getElementsByClassName("contact")[0];
    let introduction=document.getElementsByClassName("introduction")[0];
    let faq=document.getElementsByClassName("faq")[0];
    brand.addEventListener("click",()=>{window.location.href="/brand"});
    uploadstock.addEventListener("click",()=>{window.location.href="/upload"});
    bomservice.addEventListener("click",()=>{window.location.href="/bom"});
    contact.addEventListener("click",()=>{window.location.href="/contact"});
    introduction.addEventListener("click",()=>{window.location.href="/introduction"});
    index.addEventListener("click",()=>{window.location.href="/"});
    faq.addEventListener("click",()=>{window.location.href="/faq"});
}
 //每個頁面都要自動加載
window.addEventListener("load", handle_functionlist);




//function(){//程式碼}()為立即執行表達式，初始化只需要執行一次的程式
(function loadSweetAlert() {
    if (!window.Swal) {
      let script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/sweetalert2@11';
      //完成載入後執行console.log
      script.onload = function () {
        console.log('SweetAlert2 載入完成');
      };
      document.head.appendChild(script);
    }
  })();
  
  

function showalert(){
    Swal.fire('關於我的網頁','這是一個SIDE PROJECT，非用於商業用途，目的為練習網頁開發並且結合過去的工作經驗，數據來源為第三方API串接所取得','info');
}



//帳戶相關 

//註冊
function register(){
    let name=document.getElementsByClassName("register_input")[0].value;
    let email=document.getElementsByClassName("register_input")[1].value;
    let password=document.getElementsByClassName("register_input")[2].value;
    let company_name=document.getElementsByClassName("register_input")[3].value;
    let phone=document.getElementsByClassName("register_input")[4].value;
    let address=document.getElementsByClassName("register_input")[5].value;

    //檢查所有必填欄位
    if (!name || !email || !password || !company_name || !phone || !address) {
        Swal.fire('註冊失敗','請填寫所有必填欄位','error');
        return;
        }
    
    //呼叫後端註冊API
    fetch("api/user",{
        method: "POST",
        headers: {
                "Content-Type": "application/json"
            },
        body: JSON.stringify({name, email, password, company_name, phone, address})
    })
    .then(response=>{
        if (!response.ok) {
            if(response.status===400){
                console.log("已經有重複帳號");
                let displayarea=document.querySelector(".signup_link");
                displayarea.innerHTML="已經有重複帳號，請重新輸入";
            }
        }
        return response.json();
    })
    .then(data=>{
        if(data.ok){
            console.log("註冊成功");
            Swal.fire('註冊成功','請重新登入','success');
        } 
    })
    .catch(error=>{
        Swal.fire('註冊失敗', error.message, 'error');
    })
}
//登入
function login(){
    let email = document.getElementsByClassName("login_input")[0].value;
    let password = document.getElementsByClassName("login_input")[1].value;

    fetch("api/user/auth", {
        method: "PUT",
        headers: {
                "Content-Type": "application/json"
            },
        body: JSON.stringify({ email, password })
        })
    .then(response => {
        if (!response.ok) {
            if(response.status===400){
                Swal.fire('登入失敗','帳號或是密碼錯誤','error');
                return;
            }
        }
        return response.json();
        })
    .then(data => {
        if(data==undefined){
            console.log("帳號或是密碼錯誤");
        } else {
            // 同時支援不同頁面使用的 token key
            localStorage.setItem("token", data.token);
            localStorage.setItem("auth_token", data.token);
            handle_account("close");
            checkstatus();
        }
    })}
//登出
function logout(){
    let display_member = document.getElementsByClassName("user-logout")[0];
    display_member.innerHTML="";
    localStorage.setItem("token", null);
    localStorage.setItem("auth_token", null);
    window.location.href="/";
}
//確認登入狀況 非同步處理
async function checkstatus() {
    let token = getToken();
    let newheader = new Headers({
        "Authorization": token,
        "Content-Type": "application/json"
    });

    try {
        let response = await fetch("/api/user/auth", {
            method: "GET",
            headers: newheader
        });

        let data = await response.json();
        let display_login = document.querySelector(".user-icon");
        let display_logout = document.querySelector(".user-logout");

        if (data.error) {
            // 用戶未登入
            display_login.style.display = "flex";
            display_logout.style.display = "none";
            display_logout.innerHTML = "";
            return "notlogin";
        } else {
            // 用戶已登入
            display_login.style.display = "none";
            display_logout.style.display = "flex";
            display_logout.innerHTML = "登出";
            display_logout.onclick = logout;
            return 200;
        }
    } catch (error) {
        console.log(error);
        return "notlogin";
    }
}




//每個頁面都要自動加載checkstatus
window.addEventListener("load", checkstatus); 

//搜尋
function search(){
    let search_input =document.querySelector(".search-bar").value.trim();
    if (!search_input) {
        Swal.fire('查詢失敗','請填寫搜尋欄位','error');
        return;
    }
    window.location.href="/search/"+search_input+"?page=1";
}

function enter_search(event){
    if(event.key === "Enter"){
        search();
    }
}
window.addEventListener("load", () => {
    let input = document.querySelector(".search-bar");
    input.addEventListener("keydown", enter_search);
});    
