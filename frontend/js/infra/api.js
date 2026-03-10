
/*** API URL, pathの定義 ***/  
const BaseURL = "http://localhost:8000";  //"http://localhost:8000"; "http://127.0.0.1:8000"
const USERS = "/api/users"
const TASKS = "/api/tasks"
const STATS = "/api/stats/tasks-by-status"



/**
 * 例外の情報を取得する。
 * @param {object} res  fetchのレスポンスobject
 * @param {string} method  HTTPリクエストメソッド 
 * @param {string} url  アクセスしたエンドポイントURL
 */
const getAPIErrorDetail = async (res, method, url) => {
    const status = res.status;
    let detail = undefined;  

    const ct = res.headers.get("content-type") || "";
    const raw = await res.text();
    if (ct.includes("application/json")){
        try{
            const body = JSON.parse(raw);
            if(status == 422 && Array.isArray(body.detail)){
                detail = body.detail[0].msg;
            }else{
                detail = body.detail ?? body;
            }
        } catch {
            detail = raw;
        }
    } 
    else{
        detail = raw;
    }

    const err = {
        status : status,
        method : method,
        url : url,
        detail : detail
    };

    return err;

}

/**
 * ネットワークエラーの整形用
 * @param {object} e  Error Object
 * @param {string} method  HTTP request method 
 * @param {string} url  APIエンドポイントURL
 */
const makeNetworkError = (e, method, url) => {
    const error = new Error("Network Error");
    error.info = {
        status: 0,
        method,
        url,
        detail: e?.message ?? String(e)
    };

    return error;
}


const makeParseError = (e, method, url) => {
    const error = new Error("Parse Error");
    error.info = {
        status: 0,
        method,
        url,
        detail: e?.message ?? String(e)
    };

    return error;
}

const judgeErrorType = (e) => {
    if (e?.name === "AbortError") return "abort";
    if (e instanceof SyntaxError) return "parse";
    if (e instanceof TypeError) return "network";
    return "unknown";
}


/*** 共通fetch用関数 ***/ 
const request = async (method, path, query=null, payload=null) =>{
    /*** URL, pathの結合 ***/
    const absURL = `${BaseURL}${path}`;

    const headers_post = {
        "Content-Type" : "application/json"
    };
    const headers_get = {
        "Accept" : "application/json"
    };
    

    /*** GET methodのfetch実行 ***/  
    if (method === "GET") {

        let paramURL = undefined;
        if (query != null){
            const queryURL = new URLSearchParams(query).toString();
            paramURL = `${absURL}?${queryURL}`;
        } 
        else {
            paramURL = absURL;
        }
        
        try{
            const res = await fetch(paramURL, {method: method, headers: headers_get});
            if (!res.ok) {
                const err = await getAPIErrorDetail(res, method, paramURL);
                const error = new Error("HTTP Error");
                error.info = err;
                throw error;
            }

            return await res.json();
        } catch(e) {
            if(e.info){
                throw e;
            }
            const kind = judgeErrorType(e);
            if(kind === "network"){
                throw makeNetworkError(e, method, paramURL);
            }
            else if(kind === "parse"){
                throw makeParseError(e, method, paramURL);
            }
        }
    }


    /*** POST methodのfetch実行 ***/  
    else if (method === "POST") {
        try{
            const res = await fetch(absURL, {method: method, headers: headers_post, body: JSON.stringify(payload)});
            if (!res.ok) {
                const err = await getAPIErrorDetail(res, method, absURL);
                const error = new Error("HTTP Error");
                error.info = err;
                throw error;
            }

            return await res.json();
        } catch(e){
            if(e.info){
                throw e;
            }
            const kind = judgeErrorType(e);
            if(kind === "network"){
                throw makeNetworkError(e, method, absURL);
            }
            else if(kind === "parse"){
                throw makeParseError(e, method, absURL);
            }
        }
    }


    /*** PATCH methodのfetch実行 ***/  
    else if (method === "PATCH") {
        try{
            const res = await fetch(absURL, {method: method, headers: headers_post, body: JSON.stringify(payload)});
            if (!res.ok) {
                const err = await getAPIErrorDetail(res, method, absURL);
                const error = new Error("HTTP Error");
                error.info = err;
                throw error;
            }
            
            return await res.json();
        } catch(e) {
            if(e.info){
                throw e;
            }
            const kind = judgeErrorType(e);
            if(kind === "network"){
                throw makeNetworkError(e, method, absURL);
            }
            else if(kind === "parse"){
                throw makeParseError(e, method, absURL);
            }
        }
        
    }


    /*** DELETE methodのfetch実行 ***/  
    else if (method === "DELETE") {
        try{
            const res = await fetch(absURL, {method: method, headers: headers_post});
            if (!res.ok) {
                const err = await getAPIErrorDetail(res, method, absURL);
                const error = new Error("HTTP Error");
                error.info = err;
                throw error;
            }

            return true;
        } catch(e) {
            if(e.info){
                throw e;
            }
            const kind = judgeErrorType(e);
            if(kind === "network"){
                throw makeNetworkError(e, method, absURL);
            }
            else if(kind === "parse"){
                throw makeParseError(e, method, absURL);
            }
        }
    }

}




/***  エンドポイント別の関数群 ***/


/*** /api/users 関連 ***/
/**
 *userのリストを取得
 *@param {object=} queries  
 *@param {number=} queries.limit  1<= && 200>=  default=null
 *@param {number=} queries.offset  0<=  default=null
 */
const listUsers = async (queries = {}) => {
    const {limit=50, offset=0} = queries;
    const query = {"limit":limit, "offset":offset};
    const result = await request("GET", USERS, query, null);
    return result;
}


/*** user id指定取得 ***/
const getUser = async (id) => {
    const path = `${USERS}/${id}`;
    const result = await request("GET", path, null, null);

    return result;
}


/**
 * user新規作成 
 * @param {object} payload
 * @param {string} payload.name  任意の文字列  80字以下
 * @param {string} payload.email  任意の文字列  255字以下
 */
const createUser = async (payload) => {
    const result = await request("POST", USERS, null, payload);

    return result;
}


/*** /api/tasks 関連 ***/

/** 
 *  tasksのリストを取得
 * @param {object} querys 
 * @param {string=} querys.q  任意の文字列  default=null
 * @param {string=} querys.status  許可リスト["todo", "doing", "done"]   default null
 * @param {number=} querys.user_id  int 1<=  default=null
 * @param {string=} querys.due_from  ISO文字列の日付 default=null
 * @param {string=} querys.due_to  ISO文字列の日付 default=null
 * @param {string=} querys.sort  許可リスト["id","user_id","due_date","priority","created_at","updated_at"] default=null
 * @param {string=} querys.order 許可リスト["desc", "asc"] default=null
 * @param {number=} querys.limit  int 1<= default=null
 * @param {number=} querys.offset int 0<= default=null 
 */
const listTasks = async (queries = {}) => {
    
    const query = Object.fromEntries(
        Object.entries(queries).filter(([_, v]) => v != null)
    );

    const result = await request("GET", TASKS, query, null);

    return result;
}


/**
 * タスク一件（task_id）の詳細取得
 * @param {number} id  1<= must  task_id 
 */
const getTask = async (id) => {
    const path = `${TASKS}/${id}`;
    const result = await request("GET", path, null, null);

    return result;
}


/**
 * task新規作成
 * @param {*} payload 
 * @param {number} payload.user_id  1<=  must
 * @param {string} payload.title  任意の文字列  must
 * @param {string=} payload.description  任意の文字列 or null  default=null
 * @param {string} payload.status  許可リスト["todo", "doing", "done"]  default=null
 * @param {number} payload.priority  1<= && 5>=  must
 * @param {string=} payload.due_date  ISO文字列の日付  default=null
 */
const createTask = async (payload) => {
    const result = await request("POST", TASKS, null, payload);
    return result;
}


/**
 * taskの更新
 * @param {number} id  1<=  must  task_id
 * @param {object} payload 
 * @param {number=} payload.user_id  1<=  must 
 * @param {string=} payload.title  任意の文字列  default=null
 * @param {string=} payload.description  任意の文字列  default=null
 * @param {string=} payload.status  許可リスト["todo", "doing", "done"]  must
 * @param {number=} payload.priority  1<= && 5>=  must
 * @param {string=} payload.due_date  ISO文字列の日付  default=null
 */
const updateTask = async (id, payload) => {
    const path = `${TASKS}/${id}`;
    const result = await request('PATCH', path, null, payload);

    return result;
}


/**
 * taskの削除
 * @param {number} id  1<=  must  task_id
 */
const deleteTask = async (id) => {
    const path = `${TASKS}/${id}`;
    const result = await request("DELETE", path, null, null);

    return result;
}


/**
 * taskのstatus毎の集計結果を取得
 */
const getTaskStatsByStatus = async () => {
    const result = await request("GET", STATS, null, null);

    return result;
}



export {
    listUsers, getUser, createUser,
    listTasks, getTask, createTask, updateTask, deleteTask,
    getTaskStatsByStatus
};