sleep(2000)
print();
print("Replica Set Configuration Summary");
print("---------------------------------");

for (var i = 0; i < rs.conf().members.length; i++) {
    var node = rs.conf().members[i];

    print(" NODE: " + node.host);
    print(" - TAG: nodeType:" + node.tags.nodeType);
}

print();

