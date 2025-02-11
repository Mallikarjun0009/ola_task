#!/usr/bin/perl -T -w


# Copyright (C) 2014 Marc Uebel

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
use DBI;
use lib './modules';
use GestioIP;

my $daten=<STDIN> || "";
my $gip = GestioIP -> new();
my %daten=$gip->preparer("$daten");

my $client_id = $daten{'client_id'} || $gip->get_first_client_id();
my $lang = $daten{'lang'} || "";
$lang="" if $lang !~ /^\w{1,3}$/;
my $entries_per_page=$daten{'entries_per_page'} || "500";
$entries_per_page=500 if $entries_per_page !~ /^\d{1,4}$/;
my ($lang_vars,$vars_file);
($lang_vars,$vars_file,$entries_per_page)=$gip->get_lang("$entries_per_page","$lang");


# check Permissions
my @global_config = $gip->get_global_config("$client_id");
my $user_management_enabled=$global_config[0]->[13] || "";
my $locs_ro_perm = "";
my $locs_rw_perm = "";
if ( $user_management_enabled eq "yes" ) {
	my $required_perms="read_net_perm";
	($locs_ro_perm, $locs_rw_perm) = $gip->check_perms (
		client_id=>"$client_id",
		vars_file=>"$vars_file",
		daten=>\%daten,
		required_perms=>"$required_perms",
	);
}

$gip->{locs_ro_perm} = $locs_ro_perm;
$gip->{locs_rw_perm} = $locs_rw_perm;


my $rootnet=$daten{'rootnet'} || "n";
my $rootnet_num=$daten{'red_num'} || "0";
my $ip_version=$daten{'ip_version'} || "";
my $ip_version_ele = $daten{'ip_version_ele'} || "";
my $start_entry=$daten{'start_entry'} || '0';
my $tipo_ele = $daten{'tipo_ele'} || "NULL";
my $loc_ele = $daten{'loc_ele'} || "NULL";
my $order_by=$daten{'order_by'} || 'red_auf';
my $search_index=$daten{'search_index'} || '';
my $red_search=$daten{'red_search'} || '';
my $collapse_networks=$daten{'collapse_networks'} || '0';
my $bignet=$daten{bignet} || 0;


my $error_message=$gip->check_parameters(
	vars_file=>"$vars_file",
	client_id=>"$client_id",
	ip_version_ele=>"$ip_version_ele",
	ip_version=>"$ip_version",
	start_entry=>"$start_entry",
	rootnet=>"$rootnet",
	tipo_ele=>"$tipo_ele",
	loc_ele=>"$loc_ele",
	order_by=>"$order_by",
	search_index=>"$search_index",
	red_search=>"$red_search",
	collapse_networks=>"$collapse_networks",
	bignet=>"$bignet",
) || "";

$gip->print_error_with_head(title=>"$$lang_vars{gestioip_message}",headline=>"$$lang_vars{redes_dispo_message}",notification=>"$error_message",vars_file=>"$vars_file",client_id=>"$client_id") if $error_message;



my $freerange_ignore_non_root=$global_config[0]->[14] || 0;
my $global_ip_version=$global_config[0]->[5] || "v4";
if ( $global_ip_version ne "yes" ) {
	if ( $ip_version_ele ) {
		$ip_version_ele = $gip->set_ip_version_ele("$ip_version_ele");
	} else {
		$ip_version_ele = $gip->get_ip_version_ele();
	}
} else {
	$ip_version_ele = "v4";
}

#my ($collapse_networks, $show_endnet, $hide_not_rooted);
if ( defined($daten{collapse_networks}) ) {
        $collapse_networks= $daten{collapse_networks} ? 1 : 0;
        $gip->set_collapse_networks_val("1");
} elsif (( defined($daten{filter_button}) || defined($daten{pages_links_red_button})) && ! defined($daten{collapse_networks}) ) {
        $collapse_networks=0;
        $gip->set_collapse_networks_val("0");
} else {
        $collapse_networks=$gip->get_collapse_networks_val();
}

$gip->{collapse_networks} = $collapse_networks;
$gip->{freerange_ignore_non_root} = $freerange_ignore_non_root;

my ( $rootnet_ip, $rootnet_BM, $rootnet_first_ip_int, $rootnet_last_ip_int);
my @values_red;
if ( $rootnet eq "y" ) {
	@values_red = $gip->get_red("$client_id","$rootnet_num");
	$rootnet_ip = $values_red[0]->[0];
	$rootnet_BM = $values_red[0]->[1];
    if ( ! $ip_version ) {
        if ( $rootnet_ip =~ /:/ ) {
            $ip_version = "v6";
        } else {
            $ip_version = "v4";
        }
    }
	my $net_values=$gip->get_first_network_address("$client_id","$rootnet_ip","$rootnet_BM","$ip_version");
	$rootnet_first_ip_int=$net_values->{first_ip_int};
	$rootnet_last_ip_int=$net_values->{last_ip_int};

	$gip->{rootnet_first_ip} = $rootnet_ip;
	$gip->{rootnet_BM} = $rootnet_first_ip_int;
	$gip->{rootnet_first_ip_int} = $rootnet_first_ip_int;
	$gip->{rootnet_last_ip_int} = $rootnet_last_ip_int;

	$gip->CheckInput("$client_id",\%daten,"$$lang_vars{mal_signo_error_message}","$$lang_vars{rootnet_message} $rootnet_ip/$rootnet_BM","$vars_file");
} else {
	$gip->CheckInput("$client_id",\%daten,"$$lang_vars{mal_signo_error_message}","$$lang_vars{show_free_range_message}","$vars_file");
}

if ( $search_index && ! $red_search ) {
	$gip->print_error("$client_id","$$lang_vars{no_search_string_message}")
}

$gip->print_error("$client_id",$$lang_vars{formato_malo_message}) if $start_entry !~ /^\d{1,5}$/;

my $show_rootnet=$gip->get_show_rootnet_val() || "1";
my $show_endnet=$gip->get_show_endnet_val() || "1";
my $hide_not_rooted=$gip->get_hide_not_rooted_val() || "0";

my $tipo_ele_id=$gip->get_cat_net_id("$client_id","$tipo_ele") || "-1";
my $loc_ele_id=$gip->get_loc_id("$client_id","$loc_ele") || "-1";
my @ip;
my ( $anz_values_redes, $pages_links);
my $ignore_first_root_net="";


if ( $freerange_ignore_non_root == 1 && $rootnet eq "n" ) {
	if ( $collapse_networks ) {
		@ip=$gip->get_redes("$client_id","$tipo_ele_id","$loc_ele_id","$start_entry","$entries_per_page","$order_by","$ip_version_ele","1","0");
	} else {
		@ip=$gip->get_redes("$client_id","$tipo_ele_id","$loc_ele_id","$start_entry","$entries_per_page","$order_by","$ip_version_ele");
		$anz_values_redes=scalar(@ip);
	}
	$pages_links=$gip->get_pages_links_red("$client_id","$vars_file","$start_entry","$anz_values_redes","$entries_per_page","$tipo_ele","$loc_ele","$order_by","","","$show_rootnet","$show_endnet","$hide_not_rooted","$red_search");
} elsif ( $rootnet eq "n" ) {
	if ( $search_index eq "true" ) {
		@ip=$gip->search_db_red("$client_id","$vars_file",\%daten);
	} else {
		@ip=$gip->get_redes("$client_id","$tipo_ele_id","$loc_ele_id","$start_entry","$entries_per_page","$order_by","$ip_version_ele");
	}
	$anz_values_redes=scalar(@ip);
	$pages_links=$gip->get_pages_links_red("$client_id","$vars_file","$start_entry","$anz_values_redes","$entries_per_page","$tipo_ele","$loc_ele","$order_by","","","$show_rootnet","$show_endnet","$hide_not_rooted","$red_search");

} else {
	my $overlap_check_red_num = $values_red[0]->[8] || "0";
	my @overlap_redes=$gip->get_redes("$client_id","$tipo_ele_id","$loc_ele_id","$start_entry","$entries_per_page","$order_by","$ip_version_ele");
	my @overlap_found = $gip->find_overlap_redes("$client_id","$rootnet_ip","$rootnet_BM",\@overlap_redes,"$ip_version_ele","$vars_file","$rootnet","$overlap_check_red_num" );
	my @overlap_rootnets = ();
	my $i="0";
	foreach (@overlap_found) {
		push (@overlap_rootnets,$overlap_found[$i]) if $overlap_found[$i]->[10] == "1";
		$i++;
	}

	if ( $overlap_rootnets[0]->[0] ) {
		# eleminate networks from @overlap_found which are subnets of subnets with next bigger Prefix Length
		@overlap_found = sort { $a->[1] <=> $b->[1] } @overlap_found;
		my $min_overlap_BM = $overlap_found[0]->[1];

		my @overlap_rootnets_l1=();
		my $m=0;
		foreach (@overlap_rootnets) {
			$overlap_rootnets_l1[$m]->[0]=$_->[0] if $_->[1] eq "$min_overlap_BM";
			$overlap_rootnets_l1[$m]->[1]=$_->[1] if $_->[1] eq "$min_overlap_BM";
			$overlap_rootnets_l1[$m]->[3]=$_->[3] if $_->[1] eq "$min_overlap_BM";
			$overlap_rootnets_l1[$m]->[10]=$_->[10] if $_->[1] eq "$min_overlap_BM";
			$m++;
		}

		if ( $overlap_rootnets_l1[0]->[0] ) {
			$i="0";
			foreach (@overlap_rootnets_l1) {
				my $rootnet_ip_sub_l1=$overlap_rootnets_l1[$i]->[0];
				my $rootnet_BM_sub_l1=$overlap_rootnets_l1[$i]->[1];
				if ( $rootnet_ip_sub_l1 ) {
					last;
				}
				my $overlap_check_red_num_sub_l1=$overlap_rootnets_l1[$i]->[3];
				my @overlap_found_sub_l1=$gip->find_overlap_redes("$client_id","$rootnet_ip_sub_l1","$rootnet_BM_sub_l1",\@overlap_redes,"$ip_version_ele","$vars_file","1","$overlap_check_red_num_sub_l1" );
				# eleminate elements of @overlap_found_sub_l1 from @overlap_rootnets
				
				my %seen_l1 = ();
				my @new_l1 = ();
				@seen_l1{@overlap_found_sub_l1} = ();
				foreach my $item_l1 (@overlap_rootnets) {
					push(@new_l1, $item_l1) unless exists $seen_l1{$item_l1};
				}
				@overlap_rootnets = @new_l1;
				$i++;
			}
		}


		$i="0";
		## eleminate networks from @overlap_found with are subnets of rootnets of rootnets
		if ( $collapse_networks ) {
			foreach (@overlap_rootnets) {
				my $rootnet_ip_sub=$overlap_rootnets[$i]->[0];
				my $rootnet_BM_sub=$overlap_rootnets[$i]->[1];
				my $overlap_check_red_num_sub=$overlap_rootnets[$i]->[3];
				my @overlap_found_sub=$gip->find_overlap_redes("$client_id","$rootnet_ip_sub","$rootnet_BM_sub",\@overlap_redes,"$ip_version_ele","$vars_file","1","$overlap_check_red_num_sub" );
				# eleminate elements of @overlap_found_sub from @overlap_found, @new contains the elements which are in @overlap_found
				# but not in @overlap_found_sub
				
				my %seen = ();
				my @new = ();
				@seen{@overlap_found_sub} = ();
				foreach my $item (@overlap_found) {
					push(@new, $item) unless exists $seen{$item};
				}
				@overlap_found = @new;
				$i++;
			}
		}
		
		@ip=@overlap_found;
	} else {
		@ip=@overlap_found;
	}

	$anz_values_redes=scalar(@ip);

	$pages_links=$gip->get_pages_links_red("$client_id","$vars_file","$start_entry","$anz_values_redes","$entries_per_page","$tipo_ele","$loc_ele","$order_by","$rootnet","$rootnet_num");
}

if ( $ip[0]->[0] ) {
	if ( $ignore_first_root_net && $anz_values_redes == 1 && $rootnet eq "y" ) {
		print "<br><p class=\"NotifyText\">$$lang_vars{rootnet_has_no_subnets_message}</p><br>\n";
		my $rootnet_int = $gip->ip_to_int("$client_id","$rootnet_ip","$ip_version");
		my $base_uri = $gip->get_base_uri();
		my $server_proto=$gip->get_server_proto();
		my %anz_hosts_bm = $gip->get_anz_hosts_bm_hash("$client_id","$ip_version");
		my $anz_host_rootnet = $anz_hosts_bm{$rootnet_BM};
		$anz_host_rootnet =~ s/,//g;
		$anz_host_rootnet = Math::BigInt->new("$anz_host_rootnet");
		$anz_host_rootnet *= 18446744073709551616 if $rootnet_BM < 64 && $ip_version eq "v6";
		print "<form method=\"POST\" name=\"create_net\" action=\"$server_proto://$base_uri/res/ip_insertred_form.cgi\"><input name=\"client_id\" type=\"hidden\" value=\"$client_id\"><input name=\"ip_version\" type=\"hidden\" value=\"$ip_version\"><input name=\"ip\" type=\"hidden\" value=\"$rootnet_int/$anz_host_rootnet\"><input name=\"rootnet_BM\" type=\"hidden\" value=\"$rootnet_BM\"><input name=\"bignet\" type=\"hidden\" value=\"$bignet\"><p class=\"input_link_w\" onClick=\"create_net.submit()\" style=\"cursor:pointer;\" title=\"$$lang_vars{create_within_rootnet_message}\">$$lang_vars{create_message}</p></form>\n";
	} else {
		my $ip=$gip->prepare_redes_array("$client_id",\@ip,"$order_by","$start_entry","$entries_per_page","$ip_version_ele");
		$gip->PrintRedTabHead("$client_id","$vars_file","$start_entry","$entries_per_page","$pages_links","$tipo_ele","$loc_ele","$ip_version_ele","$show_rootnet","$show_endnet","$hide_not_rooted");
		$gip->PrintRedTab("$client_id",$ip,"$vars_file","simple","$start_entry","$tipo_ele","$loc_ele","$order_by","","$entries_per_page","$ip_version_ele","","","","$ignore_first_root_net");
	}

} else {
	if ( $rootnet eq "n" ) {
		print "<p class=\"NotifyText\">$$lang_vars{no_resultado_message}</p><br>\n";
	} else {
		print "<br><p class=\"NotifyText\">$$lang_vars{rootnet_has_no_subnets_message}</p><br>\n";
		my $rootnet_int = $gip->ip_to_int("$client_id","$rootnet_ip","$ip_version");
		my $base_uri = $gip->get_base_uri();
		my $server_proto=$gip->get_server_proto();
		my %anz_hosts_bm = $gip->get_anz_hosts_bm_hash("$client_id","$ip_version");
		my $anz_host_rootnet = $anz_hosts_bm{$rootnet_BM};
		$anz_host_rootnet =~ s/,//g;
		$anz_host_rootnet = Math::BigInt->new("$anz_host_rootnet");
		print "<form method=\"POST\" name=\"create_net\" action=\"$server_proto://$base_uri/res/ip_insertred_form.cgi\"><input name=\"client_id\" type=\"hidden\" value=\"$client_id\"><input name=\"ip_version\" type=\"hidden\" value=\"$ip_version\"><input name=\"ip\" type=\"hidden\" value=\"$rootnet_int/$anz_host_rootnet\"><input name=\"rootnet_BM\" type=\"hidden\" value=\"$rootnet_BM\"><input name=\"bignet\" type=\"hidden\" value=\"$bignet\"><p class=\"input_link_w\" onClick=\"create_net.submit()\" style=\"cursor:pointer;\" title=\"$$lang_vars{create_within_rootnet_message}\">$$lang_vars{create_message}</p></form>\n";
	}
}

$gip->print_end("$client_id","$vars_file","", "$daten");
