<?php
/**
 * Populates ACL tables
 */

use Newscoop\Utils\PermissionToAcl;

require_once dirname(__FILE__) . '/../../../../db_connect.php';
require_once dirname(__FILE__) . '/../../../../library/Newscoop/Utils/PermissionToAcl.php';

$roleId = 1;
$rules = array();

// update groups
$sql = 'SELECT group_id
        FROM liveuser_groups';
$groups = $g_ado_db->GetAll($sql);
foreach ($groups as $group) {
    $groupId = (int) $group['group_id'];
    $sql = "UPDATE liveuser_groups SET role_id = $roleId WHERE group_id = $groupId";
    $g_ado_db->Execute($sql);

    $sql = "SELECT right_define_name
            FROM liveuser_rights r, liveuser_grouprights g
            WHERE r.right_id = g.right_id
                AND g.group_id = $groupId";
    $rights = $g_ado_db->GetAll($sql);
    foreach ($rights as $right) {
        $rightName = $right['right_define_name'];
        list($resource, $action) = PermissionToAcl::translate($rightName);
        $rules[] = array('allow', $roleId, strtolower($resource), strtolower($action));
    }

    $roleId++;
}

// update users
$sql = 'SELECT Id
        FROM liveuser_users';
$users = $g_ado_db->GetAll($sql);
foreach ($users as $user) {
    $userId = (int) $user['Id'];
    $sql = "UPDATE liveuser_users SET role_id = $roleId WHERE Id = $userId";
    $g_ado_db->Execute($sql);

    $sql = "SELECT right_define_name
            FROM liveuser_rights r, liveuser_userrights g
            WHERE r.right_id = g.right_id
                AND g.perm_user_id = $userId";
    $rights = $g_ado_db->GetAll($sql);
    foreach ($rights as $right) {
        $rightName = $right['right_define_name'];
        list($resource, $action) = PermissionToAcl::translate($rightName);
        $rules[] = array('allow', $roleId, strtolower($resource), strtolower($action));
    }

    $roleId++;
}

if (empty($rules)) {
    return; // no rules to insert
}

$rules = array_map(function($rule) {
    list($type, $role, $resource, $action) = array_values($rule);
    return "'$type', $role, '$resource', '$action'";
}, $rules);

$sql = 'INSERT INTO acl_rule (`type`, `role_id`, `resource`, `action`) VALUES (' . implode("),\n(", $rules) . ")\n";
$g_ado_db->Execute($sql);

for ($i = 1; $i < $roleId; $i++) {
    $sql = "INSERT INTO acl_role (`id`) VALUE ( $i );";
    $g_ado_db->Execute($sql);
}