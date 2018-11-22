<?php

if (!defined('SESS_USER_VAR')){
    define('SESS_USER_VAR', 'user_model');
}

Class Base_Controller_Base {
    
    protected $_msg;
    protected $_errmsg;
    protected $_last_post;
    protected $_view;
    
    public function init(){
        $this->_msg             = isset($_SESSION["_msg"])          ? $_SESSION["_msg"]     : null;
        $this->_errmsg          = isset($_SESSION["_errmsg"])       ? $_SESSION["_errmsg"]  : null;
        $this->_last_req        = isset($_SESSION["_last_req"])     ? $_SESSION["_last_req"]  : null;
        $_SESSION["_last_req"]  = $_REQUEST;
        unset($_SESSION["_msg"]);
        unset($_SESSION["_errmsg"]);
    }
    
    public function setView(Base_View $view){
        $this->_view = $view;
    }
    
    public function set_msgs(){
        $_SESSION["_msg"]       = $this->_msg;
        $_SESSION["_errmsg"]    = $this->_errmsg;
    }
    
    protected function _check_access($resource){
    
        // check access
        if (!$_SESSION[SESS_USER_VAR]->can($resource)){
            $this->_errmsg = 'Unauthorized access.';
            $this->set_msgs();
            $location = APP_DIR."?action=home";
            header('Location: '.$location);
            exit;
        }
    }
    
}