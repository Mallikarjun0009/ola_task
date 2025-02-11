#!/usr/bin/perl -T -w

# Copyright (C) 2011 Marc Uebel

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


use strict;
use lib '../modules';
use GestioIP;
use Net::IP qw(:PROC);
use Math::BigInt;

my $daten=<STDIN> || "";
my $gip = GestioIP -> new();
my %daten=$gip->preparer($daten);

my $lang = $daten{'lang'} || "";
my ($lang_vars,$vars_file,$entries_per_page);
if ( $daten{'entries_per_page'} ) {
        $daten{'entries_per_page'} = "500" if $daten{'entries_per_page'} !~ /^\d{1,3}$/;
        ($lang_vars,$vars_file,$entries_per_page)=$gip->get_lang("$daten{'entries_per_page'}","$lang");
} else {
        ($lang_vars,$vars_file,$entries_per_page)=$gip->get_lang("","$lang");
}

my $client_id = $daten{'client_id'} || $gip->get_first_client_id();

if ( $daten{'referer'} ne "host_list_view" || $daten{BM_new} eq "32" ) {
    $gip->{print_sitebar} = 1;
    $gip->{uncheck_free_ranges} = 1;
}

my $loc_check = $daten{'loc'} || "NULL";
my $loc_id_check = $gip->get_loc_id("$client_id","$loc_check") || "";

# check Permissions
my @global_config = $gip->get_global_config("$client_id");
my $user_management_enabled=$global_config[0]->[13] || "";
my ($locs_ro_perm, $locs_rw_perm);
if ( $user_management_enabled eq "yes" ) {
	my $required_perms="read_net_perm,update_net_perm";
	($locs_ro_perm, $locs_rw_perm) = $gip->check_perms (
		client_id=>"$client_id",
		vars_file=>"$vars_file",
		daten=>\%daten,
		required_perms=>"$required_perms",
        loc_id_rw=>"$loc_id_check",
	);
}

$gip->{locs_ro_perm} = $locs_ro_perm;
$gip->{locs_rw_perm} = $locs_rw_perm;


my $global_dyn_dns_updates_enabled=$global_config[0]->[19] || "";
my $ip_version_ele = $daten{'ip_version_ele'} || ""; 

if ( $ip_version_ele eq "v6" ) {
	my $valid_v6=$gip->check_valid_ipv6("$daten{'red'}") || "0";
	if ( $valid_v6 != "1" ) {
		$gip->CheckInput("$client_id",\%daten,"$$lang_vars{mal_signo_error_message}","$$lang_vars{modificar_red_message}","$vars_file");
		$gip->print_error("$client_id","$$lang_vars{no_valid_ipv6_address_message}");
	}
} elsif ( $ip_version_ele eq "v4" ) {
	if ( $daten{'red'} !~ /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/ ) {
		$gip->CheckInput("$client_id",\%daten,"$$lang_vars{mal_signo_error_message}","$$lang_vars{modificar_red_message}","$vars_file");
		$gip->print_error("$client_id","$$lang_vars{formato_malo_message} (1)");
	}
} elsif ( $ip_version_ele eq "46" )  {
	if ( $daten{'red'} !~ /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/ ) {
		my $valid_v6=$gip->check_valid_ipv6("$daten{'red'}") || "0";
		if ( $valid_v6 != "1" ) {
			$gip->CheckInput("$client_id",\%daten,"$$lang_vars{mal_signo_error_message}","$$lang_vars{modificar_red_message}","$vars_file");
			$gip->print_error("$client_id","$$lang_vars{formato_malo_message} (2)");
		}
	}
} else {
	$gip->CheckInput("$client_id",\%daten,"$$lang_vars{mal_signo_error_message}","$$lang_vars{modificar_red_message}","$vars_file");
	$gip->print_error("$client_id","$$lang_vars{formato_malo_message} (version_ele)") if $ip_version_ele !~ /^(v4|v6|46)$/;
}

if ( $daten{BM} !~ /^\d{1,3}$/ ) {
	$gip->CheckInput("$client_id",\%daten,"$$lang_vars{mal_signo_error_message}","$$lang_vars{modificar_red_message}","$vars_file");
	$gip->print_error("$client_id","$$lang_vars{formato_bm_malo_message} (1)");
}

my $red=$daten{'red'};
my $BM=$daten{'BM'};

my $red_num = $daten{'red_num'} || "";
if ( $red_num !~ /^\d{1,5}$/ ) {
        $gip->print_init("gestioip","$$lang_vars{modificar_red_message}","$$lang_vars{modificar_red_message}","$vars_file","$client_id");
        $gip->print_error("$client_id",$$lang_vars{formato_red_malo_message}) ;
}

my ($show_rootnet, $show_endnet, $hide_not_rooted);
$show_rootnet=$gip->get_show_rootnet_val() || "1";
$show_endnet=$gip->get_show_endnet_val() || "1";
$hide_not_rooted=$gip->get_hide_not_rooted_val() || "0";


$gip->CheckInput("$client_id",\%daten,"$$lang_vars{mal_signo_error_message}","$$lang_vars{modificar_red_message}","$vars_file");

if ( $daten{BM_new} !~ /^\d{1,3}$/ ) { $gip->print_error("$client_id","$$lang_vars{formato_bm_malo_message} (2)") };
$gip->print_error("$client_id",$$lang_vars{max_signos_descr_message}) if length($daten{descr}) > 100;
$gip->print_error("$client_id",$$lang_vars{max_signos_comentario_message}) if length($daten{comentario}) > 500 ;
$gip->print_error("$client_id","$$lang_vars{formato_malo_message}") if ($daten{'referer'} !~ /^host_list_view|red_view$/ );

my $tipo_ele = $daten{'tipo_ele'} || "NULL";
my $loc_ele = $daten{'loc_ele'} || "NULL";
my $start_entry=$daten{'start_entry'} || '0';
my $order_by=$daten{'order_by'} || 'red_auf';
my $host_order_by=$daten{'host_order_by'} || 'IP_auf';
$gip->print_error("$client_id",$$lang_vars{formato_malo_message}) if $start_entry !~ /^\d{1,5}$/;
my $referer=$daten{'referer'};


$gip->print_error("$client_id","$$lang_vars{introduce_red_id_message}") if ( ! $daten{'red'} );
$gip->print_error("$client_id","$$lang_vars{introduce_BM_message}") if ( ! $daten{'BM'} );
$gip->print_error("$client_id","$$lang_vars{introduce_BM_message}") if ( ! $daten{'BM_new'} );
$gip->print_error("$client_id","$$lang_vars{introduce_description_message}") if ( ! $daten{'descr'} );
$gip->print_error("$client_id","$$lang_vars{introduce_loc_message}") if ( ! $daten{'loc'} );
$gip->print_error("$client_id","$$lang_vars{cat_red_message}") if ( ! $daten{'cat_net'} );
$gip->print_error("$client_id","$$lang_vars{formato_malo_message} (3)") if ( $global_dyn_dns_updates_enabled eq "yes" && $daten{'dyn_dns_updates'} !~ /^(1|2|3|4)$/ );


my $BM_new=$daten{'BM_new'};
$gip->print_error("$client_id","$$lang_vars{palabra_reservada_host_descr_NULL_message}") if $daten{'descr'} eq "NULL";
my $descr=$daten{'descr'} || "NULL";
$gip->print_error("$client_id","$$lang_vars{palabra_reservada_comment_NULL_message}") if $daten{'comentario'} eq "NULL";
my $comentario=$daten{'comentario'} || "NULL";
my $vigilada=$daten{'vigilada'} || "n";
my $loc=$daten{'loc'} || "NULL";
my $loc_id=$gip->get_loc_id("$client_id","$loc") || "-1";
my $cat_net=$daten{'cat_net'} || "NULL";
my $dyn_dns_updates=$daten{'dyn_dns_updates'} || 1;
my $dyn_dns_updates_audit=$dyn_dns_updates || "";


# Check SITE permission
if ( $user_management_enabled eq "yes" ) {
    $gip->check_loc_perm_rw("$client_id","$vars_file", "$locs_rw_perm", "$loc", "$loc_id");
}


my %cc_value=$gip->get_custom_columns_id_from_net_id_hash("$client_id","$red_num");
my @custom_columns = $gip->get_custom_columns("$client_id");
my $cc_anz=@custom_columns;
my %cc_mandatory_check_hash;

# prepare mandatory check
my $j=0;
foreach ( @custom_columns ) {
    my $column_name=$custom_columns[$j]->[0];
    my $mandatory=$custom_columns[$j]->[4];
    $cc_mandatory_check_hash{$column_name}++ if $mandatory;
    $j++;
}


my $event_cc = "";
my $dyn_dns_zone_name = "";
my $dyn_dns_ptr_zone_name = "";
for (my $o=0; $o<$cc_anz; $o++) {
    my $cc_name=$daten{"custom_${o}_name"} || "";
    my $cc_value=$daten{"custom_${o}_value"} || "";
    my $cc_id=$daten{"custom_${o}_id"} || "";
    if ( $cc_name eq "DNSZone" ) {
        $dyn_dns_zone_name = $cc_value;
    }
    if ( $cc_name eq "DNSPTRZone" ) {
        $dyn_dns_ptr_zone_name = $cc_value;
    }
    $event_cc = ", " . $cc_value;

    # mandatory check
    if ( exists $cc_mandatory_check_hash{$cc_name} && ! $cc_value) {
        $gip->print_error("$client_id","$$lang_vars{mandatory_field_message}: $cc_name");
    }
}

if ( $global_dyn_dns_updates_enabled eq "yes" ) {
    $gip->print_error("$client_id","$$lang_vars{no_zone_message}") if ! $dyn_dns_zone_name && $dyn_dns_updates =~ /^[23]$/;
    $gip->print_error("$client_id","$$lang_vars{no_ptr_zone_message}") if ! $dyn_dns_ptr_zone_name && $dyn_dns_updates =~ /^[24]$/;
}

my ($cc_ele, $cc_table,$cc_table_fill);

my @values_redes_old = $gip->get_red("$client_id","$red_num");
my $ip_version = "$values_redes_old[0]->[7]";
my $rootnet_val = "$values_redes_old[0]->[9]";

my $tipo_ele_id=$gip->get_cat_net_id("$client_id","$tipo_ele") || "-1";
my $loc_ele_id=$gip->get_loc_id("$client_id","$loc_ele") || "-1";

my $cat_net_id=$gip->get_cat_net_id("$client_id","$cat_net") || "-1";


my @linked_cc_id=$gip->get_custom_host_column_ids_from_name("$client_id","linkedIP");
my $linked_cc_id=$linked_cc_id[0]->[0] || "";
my %linked_cc_values=$gip->get_linked_custom_columns_hash("$client_id","$red_num","$linked_cc_id","$ip_version");

my $redob="$red/$BM_new";
my $ipob_red = new Net::IP ($redob) or $gip->print_error("$client_id","$$lang_vars{comprueba_red_BM_message}: <b>$red/$BM</b>");
my $redint=($ipob_red->intip());
my $first_ip_int = $redint;
$first_ip_int = $first_ip_int + 1 if $BM != 31;
my $broad_ip_int = ($ipob_red->last_int());
my $last_ip_int = ($ipob_red->last_int());
$last_ip_int = $last_ip_int - 1 if $BM != 31;

my $knownhosts="all";
my ($host_hash_ref,$host_sort_helper_array_ref)=$gip->get_host_hash("$client_id","$first_ip_int","$last_ip_int","$host_order_by","$knownhosts","$red_num");

if ( $BM ne $BM_new ) {
	if ( $ip_version eq "v4" ) {
#		if ( $BM_new == "31" ) { $gip->print_error("$client_id","$$lang_vars{no_bm_31_message}") };
		if ( $BM_new > "32" ) { $gip->print_error("$client_id","$$lang_vars{invalid_bitmask_message}") };
	} else {
		if ( $BM_new > "128" ) { $gip->print_error("$client_id","$$lang_vars{invalid_bitmask_message}") };
	}
	my $ip_range = new Net::IP ("$red/$BM") or $gip->print_error("$client_id","$$lang_vars{ip_malo_message}");
	my $ip_range_new = new Net::IP ("$red/$BM_new") or $gip->print_error("$client_id","BM $BM_new $$lang_vars{no_resulta_valida_message}: $$lang_vars{comprueba_red_BM_message}: <b>$red/$BM_new</b>");
	my $last_ip_int_new = "";
	$last_ip_int_new = Math::BigInt->new("$last_ip_int_new");
	$last_ip_int_new = ($ip_range_new->last_int());
	my $red_expanded=$red;
	$red_expanded = ip_expand_address ($red,6) if $ip_version eq "v6";
	if ( $rootnet_val == 0 ) {
		if ( $BM_new < 64 && $ip_version eq "v6" ) {
			$gip->print_error("$client_id","$$lang_vars{endnet_no_63_message}"); 
		}
		if ( $BM gt $BM_new ) {
			my @overlap_redes=$gip->get_overlap_red("$ip_version","$client_id");
			my @overlap_found = $gip->find_overlap_redes("$client_id","$red_expanded","$BM_new",\@overlap_redes,"$ip_version","$vars_file");
			if ( $overlap_found[1] ) {
				$gip->print_error("$client_id","$$lang_vars{rango_nuevo_message} $red/$BM_new $$lang_vars{overlaps_con_message} $overlap_found[1] - $overlap_found[0]"); 
			}
		} else {
			my $first_ip_int_del = "";
			my $last_ip_int_del = "";
			$first_ip_int_del = Math::BigInt->new("$first_ip_int_del");
			$last_ip_int_del = Math::BigInt->new("$last_ip_int_del");
			$first_ip_int_del = $last_ip_int_new + 1;
			$last_ip_int_del = ($ip_range->last_int());
			if ( $ip_version eq "v6" ) {
				$first_ip_int_del--;
				$last_ip_int_del++;
			}

			foreach my $key ( keys %$host_hash_ref ) {
				$key = Math::BigInt->new("$key");
				if ( $key >= $first_ip_int_del && $key <= $last_ip_int_del ) {
					if ( exists $linked_cc_values{$key} ) {
						my $linked_ips_delete=$linked_cc_values{$key}[0];
						$linked_ips_delete = s/^X:://;
						my $ip_ad=$linked_cc_values{$key}[1];
						my $host_id=$linked_cc_values{$key}[2];
						my @linked_ips=split(",",$linked_ips_delete);
						foreach my $linked_ip_delete(@linked_ips){
							$gip->delete_linked_ip("$client_id","$ip_version","$linked_ip_delete","$ip_ad");
						}
					}
				}
			}

			$gip->delete_custom_host_column_entry_between("$client_id","$first_ip_int_del","$last_ip_int_del","$ip_version");
			$gip->delete_ip("$client_id","$first_ip_int_del","$last_ip_int_del","$ip_version","$red_num");
		}
	} else {
		my $ignore_rootnet=0;
		my $red_check=$gip->check_red_exists("$client_id","$red_expanded","$BM_new","$ignore_rootnet");
		if ( $red_check ) {
			$gip->print_error("$client_id","$$lang_vars{red_exists_message}: <b>$red</b>");
		}
	}
	my $last_range_ip_int = "";
	my $last_ip_int_new_valid = "";
	$last_range_ip_int = Math::BigInt->new("$last_range_ip_int");
	$last_ip_int_new_valid = Math::BigInt->new("$last_ip_int_new_valid");
	$last_ip_int_new_valid = $last_ip_int_new - 1;
	my @rangos=$gip->get_rangos_red("$client_id","$red_num");
	my $i = "0";
	if ( $rangos[0]->[0] ) {
		foreach ( @rangos ) {
			if ( $rangos[$i]->[2] > $last_ip_int_new_valid ) {
				$gip->delete_range("$client_id","$rangos[$i]->[0]");
			}
			$i++;
		}
	}
	$red = ip_expand_address ($red,6) if $ip_version eq "v6";

	$gip->update_red_BM("$client_id","$red","$BM_new","$red_num","$rootnet_val", "$ip_version", "$BM");
}

$gip->update_host_loc_id("$client_id","$loc_id","$red_num");
$gip->update_redes("$client_id","$red_num","$descr","$loc_id","$vigilada","$comentario","$cat_net_id","$dyn_dns_updates");

my $event_cc_old = "";
for (my $o=0; $o<$cc_anz; $o++) {
	my $cc_name=$daten{"custom_${o}_name"} || "";
	my $cc_value=$daten{"custom_${o}_value"} || "";
	my $cc_id=$daten{"custom_${o}_id"} || "";

	next if ! $cc_name;
	
    my $cc_entry_net = "";
	if ( $daten{"custom_${o}_value"} ) {
		$cc_entry_net=$gip->get_custom_column_entry("$client_id","$red_num","$cc_name") || "";
		if ( $cc_entry_net ) {
			$gip->update_custom_column_value_red("$client_id","$cc_value{$cc_name}","$red_num","$cc_value");
		} else {
			$gip->insert_custom_column_value_red("$client_id","$cc_value{$cc_name}","$red_num","$cc_value");
		}
	} else {
		$cc_entry_net=$gip->get_custom_column_entry("$client_id","$red_num","$cc_name") || "";
		if ( $cc_entry_net ) {
			$gip->delete_custom_net_column_entry_modred("$client_id","$cc_id","$red_num","$cc_entry_net");
		}
	}

    $event_cc_old .= ", " . $cc_entry_net;
}

# TAGS

my $tag = $daten{'tag'};
my @object_tags = $gip->get_object_tags("$client_id", "$red_num", "network");
if ( $tag || @object_tags ) {
#    my @object_tags = $gip->get_object_tags("$client_id", "$red_num", "network");
    my @object_tag_ids;
    my $n=0;
    foreach (@object_tags) {
        my $id = $object_tags[$n]->[0];
        push @object_tag_ids, $id;
        $n++;
    }
    @object_tag_ids = sort { $a <=> $b } @object_tag_ids;

    my $object_tag_id_string = join("_", @object_tag_ids);

    if ( $tag ne $object_tag_id_string ) {
        foreach (@object_tag_ids) {
            my $id = $_;
            $gip->delete_tag_from_object("$client_id", "$id", "$red_num", "network");
        }
        my @new_tags = split("_", $tag);
        foreach (@new_tags) {
            my $id = $_;
            $gip->insert_tag_for_object ("$client_id", "$id", "$red_num", "network");
        }
    }
}

# ScanZones

my $scanazone = $daten{'scanazone'};
my @scanazones = $gip->get_network_scan_zones("$client_id", "$red_num","A");
if ( $scanazone || @scanazones ) {
    my @zone_ids;
    my $n=0;
    foreach (@scanazones) {
        my $id = $scanazones[$n]->[0];
        push @zone_ids, $id;
        $n++;
    }
    @zone_ids = sort { $a <=> $b } @zone_ids;

    my $zone_id_string = join("_", @zone_ids);


    if ( $scanazone ne $zone_id_string ) {
        foreach (@zone_ids) {
            my $id = $_;
            $gip->delete_scan_zone_from_net("$client_id", "$id", "$red_num", "network");
        }
        my @new_zones = split("_", $scanazone);
        foreach (@new_zones) {
            my $id = $_;
            $gip->insert_scan_zone_for_object("$client_id", "$id", "$red_num")
        }
    }
}

my $scanptrzone = $daten{'scanptrzone'};
my @scanptrzones = $gip->get_network_scan_zones("$client_id", "$red_num","PTR");
if ( $scanptrzone || @scanptrzones ) {
    my @zone_ids;
    my $n=0;
    foreach (@scanptrzones) {
        my $id = $scanptrzones[$n]->[0];
        push @zone_ids, $id;
        $n++;
    }
    @zone_ids = sort { $a <=> $b } @zone_ids;

    my $zone_id_string = join("_", @zone_ids);

    if ( $scanptrzone ne $zone_id_string ) {
        foreach (@zone_ids) {
            my $id = $_;
            $gip->delete_scan_zone_from_net("$client_id", "$id", "$red_num", "network");
        }
        my @new_zones = split("_", $scanptrzone);
        foreach (@new_zones) {
            my $id = $_;
            $gip->insert_scan_zone_for_object("$client_id", "$id", "$red_num")
        }
    }
}


my $BM_old_audit = "$values_redes_old[0]->[1]" || "";
my $descr_old_audit = "$values_redes_old[0]->[2]" || "---";
$descr_old_audit = "---" if $descr_old_audit eq "NULL";
my $loc_old_audit=$gip->get_loc_from_redid("$client_id","$red_num");
$loc_old_audit = "---" if $loc_old_audit eq "NULL";
my $vigilada_old_audit = "$values_redes_old[0]->[4]" || "n";
my $comentario_old_audit = "$values_redes_old[0]->[5]" || "---";
$comentario_old_audit = "---" if $comentario_old_audit eq "NULL";
my $cat_id_old_audit = "$values_redes_old[0]->[6]" || "---";
my $cat_old_audit=$gip->get_cat_net_from_id("$client_id","$cat_id_old_audit") || "---";
$cat_old_audit = "---" if $cat_old_audit eq "NULL";
my $dyn_dns_updates_old_audit = "$values_redes_old[0]->[10]" || "";

my $descr_audit = $descr;
$descr_audit = "---" if $descr eq "NULL";
my $comentario_audit = $comentario;
$comentario_audit = "---" if $comentario eq "NULL";

my $audit_type="2";
my $audit_class="2";
my $update_type_audit="1";
my $event="$red/$BM,$descr_old_audit,$loc_old_audit,$cat_old_audit,$comentario_old_audit,$vigilada_old_audit${event_cc_old},$dyn_dns_updates_old_audit -> $red/$BM_new,$descr_audit,$loc,$cat_net,$comentario_audit,$vigilada${event_cc},$dyn_dns_updates_audit";
$gip->insert_audit("$client_id","$audit_class","$audit_type","$event","$update_type_audit","$vars_file");


if ( $referer eq "host_list_view" && $BM_new != "32" ) {
#	print "<p><b>$$lang_vars{red_parameter_changed}</b><p>\n";
    my $div_notify = GipTemplate::create_div_notify_text(
		noti => "$$lang_vars{red_parameter_changed}",
	);
	print "$div_notify\n";

	my $anz_host_total=$gip->get_host_hash_count("$client_id","$red_num") || "0";
	my %anz_hosts_bm = $gip->get_anz_hosts_bm_hash("$client_id","$ip_version");
	my ($anz_values_hosts,$anz_values_hosts_pages);
	my ($start_entry_hosts,$entries_per_page_hosts);
	$anz_hosts_bm{$BM} =~ s/,//g;

	if ( $daten{'entries_per_page_hosts'} && $daten{'entries_per_page_hosts'} =~ /^\d{1,4}$/ ) {
		$entries_per_page_hosts=$daten{'entries_per_page_hosts'};
	} else {
		$entries_per_page_hosts = "254";
	}
	$start_entry_hosts="0";

	if ( $host_order_by =~ /IP/ ) {
		$anz_values_hosts=$entries_per_page_hosts;
		$anz_values_hosts_pages=$anz_hosts_bm{$BM};
	} else {
		$anz_values_hosts=$anz_host_total;
		$anz_values_hosts_pages=$anz_host_total;
	}

	($host_hash_ref,$first_ip_int,$last_ip_int)=$gip->prepare_host_hash("$client_id",$host_hash_ref,"$first_ip_int","$last_ip_int","res/ip_modip_form.cgi","$knownhosts","$$lang_vars{modificar_message}","$red_num","$loc","$vars_file","$anz_values_hosts","$start_entry_hosts","$entries_per_page_hosts","$host_order_by","$broad_ip_int","$ip_version");

	my $pages_links=$gip->get_pages_links_host("$client_id","$start_entry_hosts","$anz_values_hosts_pages","$entries_per_page_hosts","$red_num","$knownhosts","$host_order_by","$first_ip_int",$host_hash_ref,"$broad_ip_int","$ip_version","$vars_file","$referer");

	$gip->PrintIpTabHead("$client_id","$knownhosts","res/ip_modip_form.cgi","$red_num","$vars_file","$start_entry_hosts","$anz_values_hosts","$entries_per_page_hosts","$pages_links","$host_order_by","$ip_version");

	$gip->PrintIpTab("$client_id",$host_hash_ref,"$first_ip_int","$last_ip_int","res/ip_modip_form.cgi","$knownhosts","$$lang_vars{modificar_message}","$red_num","$loc","$vars_file","$anz_values_hosts_pages","$start_entry_hosts","$entries_per_page_hosts","$host_order_by",$host_sort_helper_array_ref,"","$ip_version");

} else {
    my $div_notify = GipTemplate::create_div_notify_text(
		noti => "$$lang_vars{redes_message} $red/$BM: $$lang_vars{red_parameter_changed}",
	);
	print "$div_notify\n";

    my $parent_network_id = $daten{parent_network_id} || "";

	if ( $parent_network_id ) {
		my @values_red = $gip->get_red("$client_id","$parent_network_id");
		my $rootnet_ip = $values_red[0]->[0];
		my $rootnet_BM = $values_red[0]->[1];
		my $net_values=$gip->get_first_network_address("$client_id","$rootnet_ip","$rootnet_BM","$ip_version_ele");
		my $rootnet_first_ip_int=$net_values->{first_ip_int};
		my $rootnet_last_ip_int=$net_values->{last_ip_int};


		$gip->{rootnet_first_ip} = $rootnet_ip;
		$gip->{rootnet_BM} = $rootnet_first_ip_int;
		$gip->{rootnet_first_ip_int} = $rootnet_first_ip_int;
		$gip->{rootnet_last_ip_int} = $rootnet_last_ip_int;
	}


    my @ip;
    if ( $parent_network_id ) {
        @ip=$gip->get_redes("$client_id","$tipo_ele_id","$loc_ele_id","$start_entry","$entries_per_page","$order_by","$ip_version_ele","$show_rootnet","$show_endnet","$hide_not_rooted","","","","$parent_network_id");
    } else {
	    @ip=$gip->get_redes("$client_id","$tipo_ele_id","$loc_ele_id","$start_entry","$entries_per_page","$order_by","$ip_version_ele","$show_rootnet","$show_endnet","$hide_not_rooted");
    }
	my $ip=$gip->prepare_redes_array("$client_id",\@ip,"$order_by","$start_entry","$entries_per_page","$ip_version_ele");

	my $anz_values_redes = scalar(@ip);
    my $pages_links=$gip->get_pages_links_red("$client_id","$vars_file","$start_entry","$anz_values_redes","$entries_per_page","$tipo_ele","$loc_ele","$order_by","","","$show_rootnet","$show_endnet","$hide_not_rooted","","$parent_network_id");

	$gip->PrintRedTabHead("$client_id","$vars_file","$start_entry","$entries_per_page","$pages_links","$tipo_ele","$loc_ele","$ip_version_ele","$show_rootnet","$show_endnet","$hide_not_rooted");
	my %changed_red_num;
	$changed_red_num{$red_num}=$red_num;
	$gip->PrintRedTab("$client_id",$ip,"$vars_file","extended","$start_entry","$tipo_ele","$loc_ele","$order_by","","$entries_per_page","$ip_version_ele","$show_rootnet","$show_endnet",\%changed_red_num,"","$hide_not_rooted");
}

$gip->print_end("$client_id","$vars_file","go_to_top", "$daten");
