/*
 * Copyright 2023 by Web3Bench Project
 * This work was based on the OLxPBench Project

 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at

 *  http://www.apache.org/licenses/LICENSE-2.0

 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.

 */

package com.olxpbenchmark.benchmarks.web3benchmark.procedures;

import com.olxpbenchmark.api.SQLStmt;
import com.olxpbenchmark.benchmarks.web3benchmark.WEB3Config;
import com.olxpbenchmark.benchmarks.web3benchmark.WEB3Constants;
import com.olxpbenchmark.benchmarks.web3benchmark.WEB3Util;
import com.olxpbenchmark.benchmarks.web3benchmark.WEB3Worker;
import com.olxpbenchmark.benchmarks.web3benchmark.procedures.WEB3Procedure;
import com.olxpbenchmark.distributions.ZipfianGenerator;
import org.apache.log4j.Logger;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Random;

public class R32 extends WEB3Procedure {

    private static final Logger LOG = Logger.getLogger(R32.class);

    // Top N transactions based on block timestamp.
    public SQLStmt query_stmtSQL = new SQLStmt(
            "select "
                    + "* "
                    + "from "
                    + "transactions "
                    + "order by "
                    + "block_timestamp desc limit 100");
    private PreparedStatement query_stmt = null;

    public ResultSet run(Connection conn, Random gen, WEB3Worker w, int startNumber, int upperLimit, int numScale,
            String nodeid) throws SQLException {
        boolean trace = LOG.isTraceEnabled();

        // initializing prepared statements
        query_stmt = this.getPreparedStatement(conn, query_stmtSQL);

        if (trace)
            LOG.trace("query_stmt R32 START");
        ResultSet rs = query_stmt.executeQuery();
        conn.commit();
        if (trace)
            LOG.trace("query_stmt R32 END");

        // Log query
        if (LOG.isDebugEnabled())
            LOG.debug(queryToString(query_stmt));
        // Log result
        if (trace)
            LOG.trace(resultSetToString(rs));

        rs.close();
        return null;
    }
}
