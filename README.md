# Procedural Town Name Generator

This project is a proof of concept for a way to procedurally generate random place names that feel like they could plausibly be places in England, without actually being places in England.

The data from which the names are generated is derived from the list of town names at [https://www.townscountiespostcodes.co.uk/](https://www.townscountiespostcodes.co.uk/) and is created by running the three python scripts in order. This results in a JSON file which is in turn used by the algorithm to generate new town names.

[Click here to generate some names!](https://local-express-limited.github.io/town-gen)

### Limitations

* Does not generate very short names like real life examples of Ely and Wem.
* Generated names might not make much sense linguistically, e.g. Cornish and Welsh prefixes combined with Anglo-Saxon and Norman suffixes can look a bit odd.

### License

Copyright (c) 2024 Mat Booth

This program and the accompanying materials are made available under the terms of the Eclipse Public License 2.0 which is available at http://www.eclipse.org/legal/epl-2.0.

This Source Code may also be made available under the following Secondary Licenses when the conditions for such availability set forth in the Eclipse Public License 2.0 are satisfied: GNU General Public License, version 2 or later with the GNU Classpath Exception.

SPDX-License-Identifier: EPL-2.0 OR GPL-2.0 WITH Classpath-exception-2.0

