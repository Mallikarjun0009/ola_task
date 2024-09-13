#!/usr/bin/perl -w -T

# Copyright (C) 2014 Marc Uebel

use strict;
use DBI;
use lib '../modules';
use GestioIP;


my $gip = GestioIP -> new();
my $daten=<STDIN> || "";
# strip # sign from the color
$daten =~ s/color=%23/color=/;
my %daten=$gip->preparer($daten);

my ($lang_vars,$vars_file)=$gip->get_lang();
my $client_id = $daten{'client_id'} || $gip->get_first_client_id();


# check Permissions
my @global_config = $gip->get_global_config("$client_id");
my $user_management_enabled=$global_config[0]->[13] || "";
if ( $user_management_enabled eq "yes" ) {
	my $required_perms="manage_gestioip_perm";
	$gip->check_perms (
		client_id=>"$client_id",
		vars_file=>"$vars_file",
		daten=>\%daten,
		required_perms=>"$required_perms",
	);
}


# Parameter check
my $server_name=$daten{'server_name'} || "";
my $user_name=$daten{'user_name'} || "";
my $password=$daten{'password'} || "";
my $default_from=$daten{'default_from'} || "";
my $security=$daten{'security'} || 0;
my $port=$daten{'port'} || "";
my $timeout=$daten{'timeout'} || "";
my $comment=$daten{'comment'} || "";


my $error_message=$gip->check_parameters(
        vars_file=>"$vars_file",
        client_id=>"$client_id",
        name=>"$server_name",
) || "";

$gip->print_error_with_head(title=>"$$lang_vars{gestioip_message}",headline=>"$$lang_vars{add_smtp_server_message}",notification=>"$error_message",vars_file=>"$vars_file",client_id=>"$client_id") if $error_message;


$gip->CheckInput("$client_id",\%daten,"$$lang_vars{mal_signo_error_message}","$$lang_vars{add_smtp_server_message}","$vars_file");

$gip->print_error("$client_id","$$lang_vars{insert_name_error_message}") if ! $server_name;
$gip->print_error("$client_id","$$lang_vars{name_no_whitespace_message}") if $server_name =~ /\s/;
$server_name=$gip->remove_whitespace_se("$server_name");
$gip->print_error("$client_id","$$lang_vars{introduce_user_password_message}") if $user_name && ! $password;

# CHECK VALID EMAIL
# check password if default_from

# Check if the object exists

my @objects = $gip->get_smtp_server("$client_id");
foreach my $obj( @objects ) {
    if ( $server_name eq $obj->[1] ) {
        $gip->print_error("$client_id","<b>$server_name</b>: $$lang_vars{smtp_server_exists_message}");
    }
}

## TEST CHECK IN USE

# Insert Object
my $last_id = $gip->insert_smtp_server("$client_id","$server_name","$user_name","$password","$default_from","$security","$port","$timeout","$comment");

print <<EOF;
<script>
update_nav_text("$$lang_vars{smtp_server_added_message}")
</script>
EOF

my $audit_type="177";
my $audit_class="34";
my $update_type_audit="1";
my $event="$server_name,$comment";
$event =~ s/,$//;

$gip->insert_audit("$client_id","$audit_class","$audit_type","$event","$update_type_audit","$vars_file");

my %changed_id;
$changed_id{$last_id}=$last_id;
$gip->PrintSMTPServerTab("$client_id","$vars_file", \%changed_id);

$gip->print_end("$client_id","$vars_file","", "$daten");

