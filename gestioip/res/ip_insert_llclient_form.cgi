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
use Net::IP;


my $daten=<STDIN> || "";
my $gip = GestioIP -> new();
my %daten=$gip->preparer($daten);

my $base_uri = $gip->get_base_uri();
my $server_proto=$gip->get_server_proto();

my $lang = $daten{'lang'} || "";
my ($lang_vars,$vars_file)=$gip->get_lang("","$lang");
my $client_id = $daten{'client_id'} || $gip->get_first_client_id();


# check Permissions
my @global_config = $gip->get_global_config("$client_id");
my $user_management_enabled=$global_config[0]->[13] || "";
if ( $user_management_enabled eq "yes" ) {
	my $required_perms="update_line_perm";
	$gip->check_perms (
		client_id=>"$client_id",
		vars_file=>"$vars_file",
		daten=>\%daten,
		required_perms=>"$required_perms",
	);
}


$gip->CheckInput("$client_id",\%daten,"$$lang_vars{mal_signo_error_message}","$$lang_vars{add_ll_client_message}","$vars_file");

my $align="align=\"right\"";
my $align1="";
my $ori="left";
my $rtl_helper="<font color=\"white\">x</font>";
if ( $vars_file =~ /vars_he$/ ) {
        $align="align=\"left\"";
        $align1="align=\"right\"";
        $ori="right";
}


print "<br><p>\n";
print "<table border=\"0\" cellpadding=\"5\" cellspacing=\"1\"><tr><td $align>";
print "$$lang_vars{ll_client_name_message}</td>\n";
print "<td><form method=\"POST\" name=\"insert_ll_client_form\" action=\"$server_proto://$base_uri/res/ip_insert_llclient.cgi\">\n";
print "<input type=\"text\" name=\"ll_client_name\" class='form-control form-control-sm m-2' style='width: 12em' size=\"10\" maxlength=\"30\"></td></tr>\n";
#print "<tr><td $align>$$lang_vars{tipo_message}</td><td $align1><input type=\"text\" name=\"type\" size=\"10\" maxlength=\"30\"></td></tr>\n";
print "<tr><td $align>$$lang_vars{comentario_message}</td><td $align1><input type=\"text\" name=\"comment\" class='form-control form-control-sm m-2' style='width: 12em' size=\"10\" maxlength=\"30\"></td></tr>\n";
print "<tr><td $align>$$lang_vars{description_message}</td><td $align1><input type=\"text\" name=\"description\" class='form-control form-control-sm m-2' style='width: 12em' size=\"10\" maxlength=\"30\"></td></tr>\n";
print "<tr><td $align>$$lang_vars{phone_message}</td><td $align1><input type=\"text\" name=\"phone\" class='form-control form-control-sm m-2' style='width: 12em' size=\"10\" maxlength=\"30\"></td></tr>\n";
print "<tr><td $align>$$lang_vars{fax_message}</td><td $align1><input type=\"text\" name=\"fax\" class='form-control form-control-sm m-2' style='width: 12em' size=\"10\" maxlength=\"30\"></td></tr>\n";
print "<tr><td $align>$$lang_vars{address_message}</td><td colspan=\"4\" $align1><textarea name=\"address\" class='form-control form-control-sm m-2'  cols=\"40\" rows=\"4\" maxlength=\"500\"></textarea></td></tr>\n";
print "<tr><td $align>$$lang_vars{contact_message}</td><td colspan='7' $align1><input type=\"text\" name=\"contact\" class='form-control form-control-sm m-2' size=\"8\" maxlength=\"30\"></td><td $align>&nbsp;&nbsp;$$lang_vars{mail_message}</td><td $align1><input type=\"text\" name=\"contact_email\" class='form-control form-control-sm m-2'  size=\"8\" maxlength=\"30\"></td><td $align>&nbsp;&nbsp;$$lang_vars{phone_message}</td><td $align1><input type=\"text\" class='form-control form-control-sm m-2'  name=\"contact_phone\" size=\"10\" maxlength=\"30\"></td><td $align>&nbsp;&nbsp;$$lang_vars{cell_message}</td><td $align1><input type=\"text\" name=\"contact_cell\" class='form-control form-control-sm m-2' size=\"10\" maxlength=\"30\"></td></tr>\n";
#print "<tr><td $align>$$lang_vars{contact_message}</td><td $align1><input type=\"text\" name=\"contact\" size=\"10\" maxlength=\"30\"></td></tr>\n";
print "<tr><td $align1><p><input type=\"hidden\" name=\"client_id\" value=\"$client_id\"><input type=\"submit\" value=\"$$lang_vars{crear_message}\" name=\"B2\" class=\"input_link_w\"></form></td><td></td></tr></table>\n";


print "<script type=\"text/javascript\">\n";
print "document.insert_ll_client_form.ll_client_name.focus();\n";
print "</script>\n";

$gip->print_end("$client_id", "", "", "");
