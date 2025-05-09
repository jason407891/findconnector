//共同頁面相關

//HEADER跟FOOTER
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

window.addEventListener("load", loadHeaderFooter); //處理HEADER跟FOOTER


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
        if(data==undefined){console.log("帳號或是密碼錯誤");}
        else{
        localStorage.setItem("token", data.token);
        handle_account("close");
        checkstatus();
        }
    })}
//登出
function logout(){
    let display_member = document.getElementsByClassName("user-logout")[0];
    display_member.innerHTML="";
    localStorage.setItem("token", null);
    window.location.href="/";
}
//確認登入狀況 非同步處理
async function checkstatus() {
    let token = localStorage.getItem("token");
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
