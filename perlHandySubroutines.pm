use strict;
use warnings;
use lib '/opt/palantir/bin/usr/local/share/perl5/';
use Cwd;

#uses awk commands to concatenate files
#is assumed that both files have titles.
sub concatenateTwoFiles {
	my ($file1, $file2, $concatenatedName) = @_;
	#first copy file1 to the new file name
	my $command = "cp $file1 $concatenatedName";
	print "executing: $command\n";
	system($command);
	#then append file2 to it, skipping the first line.
	$command = 'awk '."'".'{if (NR!=1) {print}}'."' $file2".">> $concatenatedName";
	print "executing: $command\n";
	system($command);
}

#a function that takes  a file as an argument, a string prefix and a string suffix, and executes the command via system()
#fileFilterFunction can be applied to limit the files that are returned.
sub executeCommandOnAllFilesInDirectory {
	my ($directory, $prefixString, $suffixString, $fileFilterFunction) = @_;
	if (!defined($prefixString)) {$prefixString = ""};
	if (!defined($suffixString))  {$suffixString = ""};
	if (!defined($fileFilterFunction)) {$fileFilterFunction = {return 1}};
	opendir (DIR, $directory) or die $!;
	while (my $file = readdir(DIR)) {
		if (&{$fileFilterFunction}($file)) {
			system($prefixString."$directory/$file".$suffixString);
		}	
	}		
}

sub createTitleIndexLookup { #line termination characters should have been removed by here
	my ($title, $sep) = @_;
	if (!defined($sep)) {
		$sep = "\t";
	}
	my @entries = split(/$sep/,$title);

	my $titleIndexLookup = {};
	for my $i(0..$#entries) {
		$titleIndexLookup->{$entries[$i]} = $i;
	}
	return $titleIndexLookup;
}

sub createIndexTitleLookup { #line termination characters should have been removed by here
	my ($title, $sep) = @_;
	if (!defined($sep)) {
		$sep = "\t";
	}
	my @entries = split(/$sep/,$title);

	my $titleIndexLookup = {};
	for my $i(0..$#entries) {
		$titleIndexLookup->{$i} = $entries[$i];
	}
	return $titleIndexLookup;
}


#addres $desiredPrefix to the beginning of the file (after the directory)
sub prefixFile {
	my ($filePath, $desiredPrefix) = @_;
	my $dir = &getDir($filePath);
	my $filename = &getFileName($filePath);
	my $extension = &getExtension($filePath);
	my $prefixedFile = "$dir/$desiredPrefix"."$filename.$extension";

	return $prefixedFile;
}

#accepts path to file, returns folder the file was in
#leaves the terminal / in, which can be important when concatenating this with other stuff (because this function can return a blank thing as well)
sub getDir {
	my ($pathToFile) = @_;
	my $folder = $pathToFile;
	$folder =~ s/[^\/]+$//;
	if ($folder eq $pathToFile) {
		print "couldn't pull out folder in which file lives; have you supplied a folder instead of a file? $pathToFile\n";
	}
	if ($folder !~ /^\//) {
		$folder = &getcwd."/$folder";
	}
	if ($folder eq "") {
		return &getcwd;
	}
	return $folder;
}

#everything after last / and before the last .
sub getFileName {
	my ($path) = @_;
	$path =~ s/^.*\///;
	$path =~ s/\.[^\.]*$//;
	return $path;
}

sub getExtension {
	my ($path) = @_;
	if ($path =~ /\.([^\.]+$)/) {
		return $1;
	} else {
		return "";
	}
}

sub selectRandomElementFromArray {
	my ($arr) = @_;
	my $arraySize = scalar(@{$arr});
	my $idx = int(rand($arraySize));
	return $arr->[$idx];
}

sub obtainUsernameAndPassword {
	print "Username: ";
	my $username = <STDIN>; chomp $username; #chomp removes the newline.
	system('stty -echo'); #disable password echo
	print "Password: ";
	my $password = <STDIN>; chomp $password;
	system('stty echo'); #reenable echoing
	print "\n";
	return ($username, $password);
}

#sub sendEmail {
#	my ($to,$from,$subject,$message) = @_;
#	my $msg = MIME::Lite->new(
#                 From     => $from,
#                 To       => $to,
#                 Subject  => $subject,
#                 Data     => $message
#                 );	
#	$msg->send('smtp', "mhcorpmail.molina.mhc");
#	
#}
#
return 1;
