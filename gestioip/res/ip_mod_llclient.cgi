#!/usr/bin/perl -w -T

use strict;
use DBI;
use lib '../modules';
use GestioIP;


my $gip = GestioIP -> new();
my $daten=<STDIN> || "";
my %daten=$gip->preparer($daten);

my $lang = $daten{'lang'} || "";
my ($lang_vars,$vars_file,$entries_per_page)=$gip->get_lang("","$lang");
my $base_uri = $gip->get_base_uri();

my $client_id = $daten{'client_id'} || $gip->get_first_client_id();


# check Permissions
my @global_config = $gip->get_global_config("$client_id");
my $user_management_enabled=$global_config[0]->[13] || "";
if ( $user_management_enabled eq "yes" ) {
	my $required_perms="read_line_perm,update_line_perm";
	$gip->check_perms (
		client_id=>"$client_id",
		vars_file=>"$vars_file",
		daten=>\%daten,
		required_perms=>"$required_perms",
	);
}


my $name=$daten{'name'} || "";

if ( ! $name ) {
        $gip->CheckInput("$client_id",\%daten,"$$lang_vars{mal_signo_error_message}","$$lang_vars{add_as_client_message}","$vars_file");
        $gip->print_error("$client_id","$$lang_vars{insert_as_client_name_message}");
}

$gip->CheckInput("$client_id",\%daten,"$$lang_vars{mal_signo_error_message}","$name: $$lang_vars{parameter_changed_message}","$vars_file");

$gip->print_error("$client_id","$$lang_vars{insert_ll_client_name_message}") if ! $name;

my $ll_client_id=$daten{'ll_client_id'} || "";
$gip->print_error("$client_id","$$lang_vars{formato_malo_message} (1)") if ! $ll_client_id;

my $type=$daten{'type'} || "";
my $comment=$daten{'comment'} || "";
my $description=$daten{'description'} || "";
my $phone=$daten{'phone'} || "";
my $fax=$daten{'fax'} || "";
my $address=$daten{'address'} || "";
my $contact=$daten{'contact'} || "";
my $contact_email=$daten{'contact_email'} || "";
my $contact_phone=$daten{'contact_phone'} || "";
my $contact_cell=$daten{'contact_cell'} || "";


my @values_ll_clients=$gip->get_one_ll_client("$client_id","$ll_client_id");
#my @value_ll_client=$gip->get_one_ll_client("$client_id","$ll_client_id");
#my $ll_client=$value_ll_client[0]->[1];

$gip->update_ll_client("$client_id","$ll_client_id","$name","$type","$comment","$description","$phone","$fax","$address","$contact","$contact_email","$contact_phone","$contact_cell");

my $old_name=$values_ll_clients[0]->[1] || "---";
my $old_type=$values_ll_clients[0]->[2] || "---";
my $old_description=$values_ll_clients[0]->[3] || "---";
my $old_comment=$values_ll_clients[0]->[4] || "---";
my $old_phone=$values_ll_clients[0]->[5] || "---";
my $old_fax=$values_ll_clients[0]->[6] || "---";
my $old_address=$values_ll_clients[0]->[7] || "---";
my $old_contact=$values_ll_clients[0]->[8] || "---";
my $old_contact_email=$values_ll_clients[0]->[8] || "---";
my $old_contact_phone=$values_ll_clients[0]->[8] || "---";
my $old_contact_cell=$values_ll_clients[0]->[8] || "---";
$comment = "---" if ! $comment;
$type = "---" if ! $type;
$description = "---" if ! $description;
$phone = "---" if ! $phone;
$fax = "---" if ! $fax;
$address = "---" if ! $address;
$contact = "---" if ! $contact;
$contact_email = "---" if ! $contact_email;
$contact_phone = "---" if ! $contact_phone;
$contact_cell = "---" if ! $contact_cell;
my $audit_type="58";
my $audit_class="14";
my $update_type_audit="1";
my $event1="$old_name, $old_type, $old_comment, $old_description, $old_phone, $old_fax, $old_address, $old_contact, $old_contact_email, $old_contact_phone, $old_contact_cell";
my $event2="$name, $type, $comment, $description, $phone, $fax, $address, $contact, $contact_email, $contact_phone, $contact_cell";
my $event = $event1 . " -> " . $event2;
$gip->insert_audit("$client_id","$audit_class","$audit_type","$event","$update_type_audit","$vars_file");


my @as=$gip->get_ll_clients("$client_id");

print "<p>\n";

$gip->PrintLLClientTab("$client_id",\@as,"$vars_file");

$gip->print_end("$client_id", "", "", "");

