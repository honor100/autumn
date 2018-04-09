/*
Navicat MySQL Data Transfer

Source Server         : 172.16.16.4_4001
Source Server Version : 50718
Source Host           : 172.16.16.4:4001
Source Database       : overprotect

Target Server Type    : MYSQL
Target Server Version : 50718
File Encoding         : 65001

Date: 2018-04-06 11:51:38
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for overprotect_fingerprint
-- ----------------------------
DROP TABLE IF EXISTS `overprotect_fingerprint`;
CREATE TABLE `overprotect_fingerprint` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键',
  `sql_template` text NOT NULL COMMENT 'sql模板',
  `fingerprint` char(32) NOT NULL DEFAULT '' COMMENT 'sql指纹',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间--sql第一次出现的时间',
  `update_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00' ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间--sql最近一次出现的时间',
  `amount` int(10) unsigned NOT NULL DEFAULT '1' COMMENT '总数',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_fingerprint` (`fingerprint`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of overprotect_fingerprint
-- ----------------------------
INSERT INTO `overprotect_fingerprint` VALUES ('1', 'select id from rz_activity.rz_additional_user_red_envelope r\n        where r.end_time < now()\n        and r.`status` in (?,?,?)  order by id desc\n        limit ? ,?', '152238645c06e014cd7be194e3d628e6', '2018-01-23 22:30:12', '2018-01-24 18:30:25', '7');
INSERT INTO `overprotect_fingerprint` VALUES ('2', 'select  a.user_id\n    from  rz_borrow.rz_borrow_collection  a\n    inner  join  rz_borrow.rz_borrow  b  on  a.borrow_id  =  b.id\n    where  a.`status`  in  (?,?,?)\n    and  b.full_time  !=\'?\'\n    and  b.full_time < current_date\n    and  a.repayment_time   >=  curdate()      and    b.id!=?', '951ab0555bef8431b6aca601bdd5003b', '2018-01-24 00:00:40', '2018-01-24 00:00:55', '2');
INSERT INTO `overprotect_fingerprint` VALUES ('6', 'delete from rz_compare.rz_bob_account_data', '6ac19f5fe5f5b9f4f055d8c910119dac', '2018-01-24 12:43:56', '2018-01-24 12:44:57', '5');

-- ----------------------------
-- Table structure for overprotect_logs
-- ----------------------------
DROP TABLE IF EXISTS `overprotect_logs`;
CREATE TABLE `overprotect_logs` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `host` varchar(50) NOT NULL DEFAULT '127.0.0.1',
  `port` smallint(5) unsigned NOT NULL DEFAULT '3306',
  `query_time` int(7) NOT NULL DEFAULT '0',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `query_id` bigint(4) NOT NULL DEFAULT '0',
  `user` varchar(16) NOT NULL DEFAULT '',
  `client_host` varchar(64) NOT NULL DEFAULT '',
  `db` varchar(64) NOT NULL DEFAULT '',
  `command` varchar(16) NOT NULL DEFAULT '',
  `time` int(7) NOT NULL DEFAULT '0',
  `state` varchar(64) NOT NULL DEFAULT '',
  `info` text,
  `fingerprint_id` int(11) NOT NULL DEFAULT '0' COMMENT '关联overprotect_fingerprint表主键id',
  PRIMARY KEY (`id`),
  KEY `idx_create_time` (`create_time`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of overprotect_logs
-- ----------------------------

-- ----------------------------
-- Table structure for overprotect_logs_201801
-- ----------------------------
DROP TABLE IF EXISTS `overprotect_logs_201801`;
CREATE TABLE `overprotect_logs_201801` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `host` varchar(50) NOT NULL DEFAULT '127.0.0.1',
  `port` smallint(5) unsigned NOT NULL DEFAULT '3306',
  `query_time` int(7) NOT NULL DEFAULT '0',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `query_id` bigint(4) NOT NULL DEFAULT '0',
  `user` varchar(16) NOT NULL DEFAULT '',
  `client_host` varchar(64) NOT NULL DEFAULT '',
  `db` varchar(64) NOT NULL DEFAULT '',
  `command` varchar(16) NOT NULL DEFAULT '',
  `time` int(7) NOT NULL DEFAULT '0',
  `state` varchar(64) NOT NULL DEFAULT '',
  `info` text NOT NULL,
  `fingerprint_id` int(11) NOT NULL DEFAULT '0' COMMENT '关联overprotect_fingerprint表主键id',
  PRIMARY KEY (`id`),
  KEY `idx_create_time` (`create_time`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of overprotect_logs_201801
-- ----------------------------
INSERT INTO `overprotect_logs_201801` VALUES ('1', '172.16.103.141', '5000', '10', '2018-01-23 22:30:12', '2752', 'mycat_rzp2p', '172.16.102.144:36887', 'rz_account', 'Query', '12', 'Sending data', 'SELECT id FROM rz_activity.rz_additional_user_red_envelope r\n        WHERE r.end_time < NOW()\n        AND r.`status` IN (0,2,7)  ORDER BY id DESC\n        limit 0 ,500', '1');
INSERT INTO `overprotect_logs_201801` VALUES ('2', '172.16.104.141', '5000', '10', '2018-01-24 00:00:40', '2568', 'mycat_rzp2p', '172.16.101.144:46497', 'rz_account', 'Query', '13', 'Sending data', 'SELECT  a.user_id\n    from  rz_borrow.rz_borrow_collection  a\n    INNER  JOIN  rz_borrow.rz_borrow  b  on  a.borrow_id  =  b.id\n    where  a.`status`  in  (0,1,2)\n    and  b.full_time  !=\'0000-00-00  00:00:00\'\n    and  b.full_time < CURRENT_DATE\n    and  a.repayment_time   >=  CURDATE()      and    b.id!=10000', '2');
INSERT INTO `overprotect_logs_201801` VALUES ('3', '172.16.104.141', '5000', '10', '2018-01-24 00:00:55', '2568', 'mycat_rzp2p', '172.16.101.144:46497', 'rz_account', 'Query', '28', 'Sending data', 'SELECT  a.user_id\n    from  rz_borrow.rz_borrow_collection  a\n    INNER  JOIN  rz_borrow.rz_borrow  b  on  a.borrow_id  =  b.id\n    where  a.`status`  in  (0,1,2)\n    and  b.full_time  !=\'0000-00-00  00:00:00\'\n    and  b.full_time < CURRENT_DATE\n    and  a.repayment_time   >=  CURDATE()      and    b.id!=10000', '2');
INSERT INTO `overprotect_logs_201801` VALUES ('4', '172.16.103.141', '5000', '10', '2018-01-24 06:30:14', '4217', 'mycat_rzp2p', '172.16.102.144:40727', 'rz_account', 'Query', '14', 'Sending data', 'SELECT id FROM rz_activity.rz_additional_user_red_envelope r\n        WHERE r.end_time < NOW()\n        AND r.`status` IN (0,2,7)  ORDER BY id DESC\n        limit 0 ,500', '1');
INSERT INTO `overprotect_logs_201801` VALUES ('5', '172.16.102.141', '5000', '10', '2018-01-24 08:30:11', '3618', 'mycat_rzp2p', '172.16.102.144:23221', 'rz_account', 'Query', '12', 'Sending data', 'SELECT id FROM rz_activity.rz_additional_user_red_envelope r\n        WHERE r.end_time < NOW()\n        AND r.`status` IN (0,2,7)  ORDER BY id DESC\n        limit 0 ,500', '1');
INSERT INTO `overprotect_logs_201801` VALUES ('6', '172.16.101.141', '5000', '10', '2018-01-24 12:43:56', '40521', 'mycat_rzp2p', '172.16.101.144:63109', 'rz_account', 'Query', '20', 'updating', 'delete from rz_compare.rz_bob_account_data', '6');
INSERT INTO `overprotect_logs_201801` VALUES ('7', '172.16.101.141', '5000', '10', '2018-01-24 12:44:11', '40521', 'mycat_rzp2p', '172.16.101.144:63109', 'rz_account', 'Query', '35', 'updating', 'delete from rz_compare.rz_bob_account_data', '6');
INSERT INTO `overprotect_logs_201801` VALUES ('8', '172.16.101.141', '5000', '10', '2018-01-24 12:44:26', '40521', 'mycat_rzp2p', '172.16.101.144:63109', 'rz_account', 'Query', '50', 'updating', 'delete from rz_compare.rz_bob_account_data', '6');
INSERT INTO `overprotect_logs_201801` VALUES ('9', '172.16.101.141', '5000', '10', '2018-01-24 12:44:42', '40521', 'mycat_rzp2p', '172.16.101.144:63109', 'rz_account', 'Query', '66', 'updating', 'delete from rz_compare.rz_bob_account_data', '6');
INSERT INTO `overprotect_logs_201801` VALUES ('10', '172.16.101.141', '5000', '10', '2018-01-24 12:44:57', '40521', 'mycat_rzp2p', '172.16.101.144:63109', 'rz_account', 'Query', '81', 'query end', 'delete from rz_compare.rz_bob_account_data', '6');
INSERT INTO `overprotect_logs_201801` VALUES ('11', '172.16.104.141', '5000', '10', '2018-01-24 16:30:13', '6585', 'mycat_rzp2p', '172.16.101.144:57013', 'rz_account', 'Query', '13', 'Sending data', 'SELECT id FROM rz_activity.rz_additional_user_red_envelope r\n        WHERE r.end_time < NOW()\n        AND r.`status` IN (0,2,7)  ORDER BY id DESC\n        limit 0 ,500', '1');
INSERT INTO `overprotect_logs_201801` VALUES ('12', '172.16.103.141', '5000', '10', '2018-01-24 16:30:28', '6856', 'mycat_rzp2p', '172.16.101.144:7189', 'rz_account', 'Query', '11', 'Sending data', 'SELECT id FROM rz_activity.rz_additional_user_red_envelope r\n        WHERE r.end_time < NOW()\n        AND r.`status` IN (0,2,7)  ORDER BY id DESC\n        limit 500 ,500', '1');
INSERT INTO `overprotect_logs_201801` VALUES ('13', '172.16.102.141', '5000', '10', '2018-01-24 18:30:10', '4032', 'mycat_rzp2p', '172.16.102.144:24299', 'rz_account', 'Query', '10', 'Sending data', 'SELECT id FROM rz_activity.rz_additional_user_red_envelope r\n        WHERE r.end_time < NOW()\n        AND r.`status` IN (0,2,7)  ORDER BY id DESC\n        limit 0 ,500', '1');
INSERT INTO `overprotect_logs_201801` VALUES ('14', '172.16.103.141', '5000', '10', '2018-01-24 18:30:25', '4695', 'mycat_rzp2p', '172.16.102.144:41981', 'rz_account', 'Query', '13', 'Sending data', 'SELECT id FROM rz_activity.rz_additional_user_red_envelope r\n        WHERE r.end_time < NOW()\n        AND r.`status` IN (0,2,7)  ORDER BY id DESC\n        limit 500 ,500', '1');

-- ----------------------------
-- Table structure for overprotect_policy
-- ----------------------------
DROP TABLE IF EXISTS `overprotect_policy`;
CREATE TABLE `overprotect_policy` (
  `id` smallint(5) unsigned NOT NULL AUTO_INCREMENT,
  `host` varchar(50) NOT NULL DEFAULT '127.0.0.1' COMMENT '主机: ip,域名',
  `port` smallint(5) unsigned NOT NULL DEFAULT '3306' COMMENT '端口',
  `db` varchar(50) NOT NULL DEFAULT '["%"]' COMMENT '被保护库: % 所有库',
  `query_type` tinyint(4) unsigned NOT NULL DEFAULT '1' COMMENT '查询类型: 1 Query,2 Sleep,12 Query Sleep',
  `query_time` smallint(3) unsigned NOT NULL DEFAULT '30' COMMENT '查询时间',
  `batch` tinyint(3) unsigned NOT NULL DEFAULT '20' COMMENT '批量查杀数量',
  `sleep` float(3,1) unsigned NOT NULL DEFAULT '0.1' COMMENT '查杀间隔',
  `start_time` time NOT NULL DEFAULT '00:00:00' COMMENT '开始时间',
  `end_time` time NOT NULL DEFAULT '23:59:59' COMMENT '结束时间',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '创建时间',
  `kill_or_not` tinyint(3) unsigned NOT NULL DEFAULT '1' COMMENT '查杀状态: 0 stop kill, 1 start kill',
  `mail_alarm` tinyint(3) unsigned NOT NULL DEFAULT '1' COMMENT '邮件告警: 0 off, 1 on',
  `msg_alarm` tinyint(3) unsigned NOT NULL DEFAULT '0' COMMENT '邮件告警: 0 off, 1 on',
  `status` tinyint(3) unsigned NOT NULL DEFAULT '1' COMMENT '策略状态: 0 off, 1 on',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_host_port` (`host`,`port`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of overprotect_policy
-- ----------------------------
INSERT INTO `overprotect_policy` VALUES ('1', '172.16.101.141', '5000', '[\"%\"]', '1', '10', '20', '0.1', '00:00:00', '23:59:59', '2018-01-23 19:34:17', '0', '0', '0', '1');
INSERT INTO `overprotect_policy` VALUES ('2', '172.16.102.141', '5000', '[\"%\"]', '1', '10', '20', '0.1', '00:00:00', '23:59:59', '2018-01-23 19:34:20', '0', '0', '0', '1');
INSERT INTO `overprotect_policy` VALUES ('3', '172.16.103.141', '5000', '[\"%\"]', '1', '10', '20', '0.1', '00:00:00', '23:59:59', '2018-01-23 19:34:26', '0', '0', '0', '1');
INSERT INTO `overprotect_policy` VALUES ('4', '172.16.104.141', '5000', '[\"%\"]', '1', '10', '20', '0.1', '00:00:00', '23:59:59', '2018-01-23 19:34:29', '0', '0', '0', '1');
INSERT INTO `overprotect_policy` VALUES ('5', '172.16.101.142', '5001', '[\"%\"]', '1', '10', '20', '0.1', '00:00:00', '23:59:59', '2018-01-23 19:34:29', '0', '0', '0', '1');
INSERT INTO `overprotect_policy` VALUES ('6', '172.16.102.142', '5001', '[\"%\"]', '1', '10', '20', '0.1', '00:00:00', '23:59:59', '2018-01-23 19:34:33', '0', '0', '0', '1');

-- ----------------------------
-- Table structure for overprotect_whitelist_db
-- ----------------------------
DROP TABLE IF EXISTS `overprotect_whitelist_db`;
CREATE TABLE `overprotect_whitelist_db` (
  `id` smallint(5) unsigned NOT NULL AUTO_INCREMENT,
  `host` varchar(50) NOT NULL DEFAULT '127.0.0.1',
  `port` smallint(5) unsigned NOT NULL DEFAULT '3306',
  `db` varchar(64) NOT NULL DEFAULT 'all',
  `start_time` time NOT NULL DEFAULT '09:00:00',
  `end_time` time NOT NULL DEFAULT '18:00:00',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `status` tinyint(3) unsigned NOT NULL DEFAULT '1' COMMENT '0 stop filter, 1 start filter',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_host_port_db` (`host`,`port`,`db`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of overprotect_whitelist_db
-- ----------------------------

-- ----------------------------
-- Table structure for overprotect_whitelist_user
-- ----------------------------
DROP TABLE IF EXISTS `overprotect_whitelist_user`;
CREATE TABLE `overprotect_whitelist_user` (
  `id` smallint(5) unsigned NOT NULL AUTO_INCREMENT,
  `host` varchar(50) NOT NULL DEFAULT '127.0.0.1',
  `port` smallint(5) unsigned NOT NULL DEFAULT '3306',
  `user` varchar(16) NOT NULL DEFAULT 'all',
  `start_time` time NOT NULL DEFAULT '09:00:00',
  `end_time` time NOT NULL DEFAULT '18:00:00',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `status` tinyint(3) unsigned NOT NULL DEFAULT '1' COMMENT '0 stop filter, 1 start filter',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_host_port_user` (`host`,`port`,`user`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of overprotect_whitelist_user
-- ----------------------------

-- ----------------------------
-- Table structure for product_info
-- ----------------------------
DROP TABLE IF EXISTS `product_info`;
CREATE TABLE `product_info` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键',
  `product` varchar(20) NOT NULL DEFAULT '' COMMENT '产品线',
  `port` smallint(5) unsigned NOT NULL DEFAULT '0' COMMENT '端口',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_port` (`port`) USING BTREE,
  UNIQUE KEY `uniq_product` (`product`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of product_info
-- ----------------------------
INSERT INTO `product_info` VALUES ('1', '老项目库', '3306');
