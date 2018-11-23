<?php

abstract class Base_Model {

    abstract protected function _insert();
    abstract protected function _update();
    abstract protected function _select_sql($single = false, $cnt_only = false);
    abstract public function read($id);
    abstract public function from_array($array);
    
    public function __get($name)
    {
        $var = '_'.$name;
        if (isset($this->$var)){
            return $this->$var;
        }
        return null;
    }
    
    public function get_all(){
        return $this->_get_all();
    }

    protected function _get_one($conditions = null, $order = null){
        $result = $this->_get_all($conditions, false, $order, 1, null);
        if (empty($result)){
            return array();
        }
        reset($result);
        return current($result);
    }
    
    protected function _get_all($conditions = null, $cnt_only = false, $order = null, $limit = null, $offset = null, $select = null) {
        
        $mysqli = $this->_get_db_connection();

        if (null === $select){
            $select = $this->_select_sql(false, $cnt_only);
        }

        if (null !== $conditions){
            $select .= ' WHERE '.$conditions;
        }
        
        if (null !== $order){
            $select .= ' ORDER BY '.$order;
        }
        
        if (null !== $limit){
            $select .= ' LIMIT '.$limit;
        }
        
        if (null !== $offset){
            $select .= ' OFFSET '.$offset;
        }
        
        $result     = $mysqli->query($select);
        $db_result  = null;
        if (false !== $result && $result->num_rows) {
            if ($cnt_only){
                $row = $result->fetch_assoc();
                $db_result = $row['cnt'];
            } else {
                $db_result = array();
                while ($row = $result->fetch_assoc()){
                    $db_result[$row['id']] = $row;
                }
            }
            $result->free();
        }
        $mysqli->close();
        return $db_result;
        
    }
    public function save(){
    
        if ($this->_id){
            return $this->_update();
        }
        return $this->_insert();
    }
    
    protected function _get_db_connection($block = 'prod', $config_file = null) {
    
        if (null === $config_file){
            $config_file = WEBROOT.'config/db.php';
        }
        
        include $config_file;
        
        if (null === $block){
            $block = ENVIRONMENT;
        }
        
        $config = $config_db[$block];
        
        $mysqli = new mysqli($config['db_server'], $config['db_user'], $config['db_pass'], $config['db_name']);
    
        if ($mysqli->connect_error) {
            die('Connect Error (' . $mysqli->connect_errno . ') '
                . $mysqli->connect_error);
        }
    
        $mysqli->query("SET NAMES utf8");
        $mysqli->query("SET `time_zone` = '".date('P')."'");
        return $mysqli;
    }
    
}

?>