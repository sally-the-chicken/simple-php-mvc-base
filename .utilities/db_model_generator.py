#!/usr/bin/env python
# -*- coding: utf-8 -*-

import lib, getopt, sys

def gen_model_for_tbl(dbsection, tablename, classname):
    """Generate model for table"""
    cols = lib.get_cols_for_tbl(tablename, dbsection)
    blocks = {'variable':'', '_insert':'', '_update':'', '_select_sql':'', 'read':'', 'from_array':''}
    colnames = []
    insert_cols = []
    insert_vals = []
    insert_bind_cols = []
    insert_bind_types = []
    update_col_vals = []
    update_bind_cols = []
    update_bind_types = []
    select_join_txt = "`, \".\n   \""+classname+".`"
    read_join_txt1 = "'=>null,'"
    read_join_txt2 = "'],$"+classname+"['"
    read_arr_txt1 = ''
    insert_arr_txt = ''
    for col in cols:
        colname = col['name'].decode('utf-8')
        coltype = col['type'].decode('utf-8')
        if col['default'] is None:
            default = 'null'
        elif col['default'] == 'CURRENT_TIMESTAMP':
            default = 'date("Y-m-d H:i:s")'
        else:
            default = "'%s'" % col['default'].decode('utf-8')
        colnames.append(colname)
        clean_colname = colname.replace('-', '_')
        blocks['variable'] += "    protected $_%s;\n" % clean_colname
        blocks['from_array'] += "        $this->_%s = isset($%s['%s'])  ? $%s['%s'] : %s;\n" % (clean_colname, classname, colname, classname, colname, default)
        read_arr_txt1 += "        $this->_%s = $%s['%s'];\n" % (clean_colname,classname,colname)
        insert_arr_txt += "        $%s = $this->_%s;\n" % (clean_colname,clean_colname)
        if (colname <> 'id' and 'modified' not in colname):
            insert_cols.append(colname)
            if (colname == 'created_date'):
                insert_vals.append('NOW()')
            else:
                insert_vals.append('?')
                insert_bind_cols.append(colname)
                if ('int' in coltype):
                    insert_bind_types.append('i')
                else:
                    insert_bind_types.append('s')
        
        if (colname <> 'id' and 'created' not in colname):
            if (colname == 'modified_date'):
                update_col_vals.append("`modified_date` = NOW()")
            else:
                update_col_vals.append("`"+colname+"` = ?")
                update_bind_cols.append(clean_colname)
                if ('int' in coltype):
                    update_bind_types.append('i')
                else:
                    update_bind_types.append('s')
    
    #### select_sql ####
    blocks['_select_sql'] = "   \""+classname+".`" + select_join_txt.join(colnames) + "`\".\n"
    blocks['_select_sql'] = """
        $select = "SELECT ";
        if ($single){
            $select .= %s
            "FROM %s AS %s ";
            return $select;
        }
        if ($cnt_only){
            $select .= " count(*) as cnt ";
        } else {
            $select .= $this->_getSelectComplete();
        }
        return $select;""" % (blocks['_select_sql'],tablename,classname)
    blocks['_select_sql'] = "protected function _select_sql($single = false, $cnt_only = false){\n%s\n}" % blocks['_select_sql']

    #### read ####
    read_txt1 = "$"+classname+" = array('"+read_join_txt1.join(colnames)+"'=>null);"
    read_txt2 = "$stmt->bind_result($"+classname+"['"+read_join_txt2.join(colnames)+"']);"
    
    blocks['read'] = """
    public function read($id){
        
        $select  = $this->_select_sql(true);
        $select .= " WHERE `id` = ?";

        $mysqli = $this->_get_db_connection();
        if (!$stmt = $mysqli->prepare($select)){
            throw new Exception("Prepare statement failed.\\nQuery: $select \\n{$mysqli->error}\\n\\n");
        }
        $stmt->bind_param('i', $id);
        if (false === ($result = $stmt->execute())){
            throw new Exception("Execute statement failed.\\nQuery: $select \\n{$mysqli->error}\\n\\n");
        }
        $stmt->store_result();
        if ($stmt->num_rows == 0){
            return false;
        }
        %s
        %s
        $stmt->fetch();
        $stmt->free_result();
        $stmt->close();
        $mysqli->close();
        %s
        return true;
        }
        """ % (read_txt1,read_txt2,read_arr_txt1)
        
    ####insert ####
    insert_txt1 = '`'+"`,`".join(insert_cols)+'`'
    insert_txt2 = ",".join(insert_vals)
    insert_bind_type_txt = "".join(insert_bind_types)
    insert_bind_col_txt = "$"+",$".join(insert_bind_cols)
    blocks['_insert'] = """
    protected function _insert(){

        $insert = "INSERT INTO `%s` (%s) ".
                "VALUES (%s)";
        $mysqli = $this->_get_db_connection();
        if (!$stmt = $mysqli->prepare($insert)){
            throw new Exception("Prepare statement failed.\\nQuery: $insert \\n{$mysqli->error}\\n\\n");
        }
        %s
        $db_result = $stmt->bind_param('%s',%s);
        if (false === $db_result){
            throw new Exception("Bind statement failed.\\nQuery: $insert \\n{$mysqli->error}\\n\\n");
        }
        if (false === ($result = $stmt->execute())){
            throw new Exception("Execute statement failed.\\nQuery: $insert \\n{$mysqli->error}\\n\\n");
        }
        $this->_id = $mysqli->insert_id;
        return $result;
    }
    """ % (tablename,insert_txt1,insert_txt2,insert_arr_txt,insert_bind_type_txt,insert_bind_col_txt)
    
    #### update ####
    update_txt1 = ",".join(update_col_vals)
    update_bind_type_txt = "".join(update_bind_types)+"i"
    update_bind_col_txt = "$"+",$".join(update_bind_cols)+",$id"
    blocks['_update'] = """
    protected function _update(){

        $update = "UPDATE `%s` SET ".
                "%s".
                " WHERE `id` = ?";
        
        $mysqli = $this->_get_db_connection();
        if (!$stmt = $mysqli->prepare($update)){
            throw new Exception("Prepare statement failed.\\nQuery: $update \\n{$mysqli->error}\\n\\n");
        }
        %s
        
        $stmt->bind_param('%s',%s);
        if (false === ($result = $stmt->execute())){
            throw new Exception("Execute statement failed.\\nQuery: $update \n{$mysqli->error}\\n\\n");
        }
        return $result;
    }
    """ % (tablename, update_txt1, insert_arr_txt, update_bind_type_txt, update_bind_col_txt)
    blocks['from_array'] = "    public function from_array($%s){\n%s\n       return $this;\n    }" % (classname, blocks['from_array'])
    return blocks


def main(argv):
    """ Main function: e.g. ./db_model_generator.py -d cms-news -t articles -c article """
    dbsect = table_name = class_name = ''
    try:
        opts, args = getopt.getopt(argv,"hd:t:c:",["dbsect=","table=","class="])
    except getopt.GetoptError:
        print './db_model_generator.py -d <db_section> -t <table> -c <classname>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print './db_model_generator.py -d <db_section> -t <table> -c <classname>'
            sys.exit()
        elif opt in ("-d", "--dbsect"):
            dbsect = arg
        elif opt in ("-t", "--table"):
            table_name = arg
        elif opt in ("-c", "--class"):
            class_name = arg
    print 'DB section is ', dbsect
    print 'Table is ', table_name
    print 'Classname is ', class_name

    result = gen_model_for_tbl(dbsect, table_name, class_name)
    for (k, v) in result.iteritems():
        print k
        print v

if __name__ == "__main__":
   main(sys.argv[1:])
